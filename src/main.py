import json
import argparse
import time
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup
from openai import OpenAI
from anthropic import Anthropic

from src.config import settings
from src.logger import logger


class LangdingTranslator:
    """Main translator class for Langding application."""

    def __init__(self, input_dir: str, output_dir: str, template_dir: str = "templates"):
        """Initialize the translator with directories."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.template_dir = Path(template_dir)

        # Initialize AI client based on provider
        if settings.AI_PROVIDER.lower() == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.provider = "anthropic"
        else:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.provider = "openai"

        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_from_html(self, html_file: Path) -> List[str]:
        """
        Extract all text content from an HTML file.

        Args:
            html_file: Path to the HTML file to parse.

        Returns:
            List of text strings extracted from the HTML file.
        """
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract meaningful text blocks, prioritizing important content
        texts = []
        important_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "title", "meta"]

        # First, get important content from specific tags
        for tag in important_tags:
            elements = soup.find_all(tag)
            for element in elements:
                if tag == "meta" and element.get("name") == "description":
                    content = element.get("content", "").strip()
                    if content and len(content) > 10:
                        texts.append(content)
                elif tag == "title":
                    content = element.get_text().strip()
                    if content and len(content) > 3:
                        texts.append(content)
                else:
                    content = element.get_text().strip()
                    # Only meaningful content (sentences or phrases)
                    if content and (len(content) > 10 or " " in content):
                        texts.append(content)

        # Remove duplicates while preserving order
        seen = set()
        unique_texts = []
        for text in texts:
            if text not in seen and len(text.strip()) > 0:
                seen.add(text)
                unique_texts.append(text)

        return unique_texts[:15]  # Limit to 15 most important texts for speed

    def create_template(self, html_file: Path, placeholders_dict: Dict[str, str]) -> Path:
        """
        Create a template HTML file where text is replaced by placeholders.

        Args:
            html_file: Path to the original HTML file.
            placeholders_dict: Mapping of an original text to placeholders.

        Returns:
            Path to the generated template HTML file.
        """
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # Replace text with placeholders
        for text, placeholder in placeholders_dict.items():
            for element in soup.find_all(string=lambda s: s and s.strip() == text):
                element.replace_with(f"{{{{{placeholder}}}}}")

        # Save template
        template_filename = f"template_{html_file.name}"
        template_path = self.output_dir / template_filename

        with open(template_path, "w", encoding="utf-8") as file:
            file.write(str(soup.prettify()))

        logger.info(f"Created template: {template_path}")
        return template_path

    def translate_text_with_context(self, text: str, target_language: str, context: str) -> str:
        """
        Translate text to target language using AI API with context.

        Args:
            text: Text to translate.
            target_language: Target language name.
            context: Context for better translation.

        Returns:
            Translated text.
        """
        try:
            prompt = (
                f"{context}\n\n"
                f'Text to translate: "{text}"\n\n'
                f"Return ONLY the translated text in {target_language}. "
                f"Keep technical terms, proper names, and brand names unchanged. "
                f"Maintain the original formatting and tone."
            )

            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=500,
                    temperature=0.3,
                    system="You are a professional translator. Provide only the translation without any explanations.",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()
            else:
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Provide only the translation without any explanations.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=500,
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Translation error for '{text}': {e}")
            return text  # Return original text on error

    def generate_language_files(
        self,
        translations: Dict[str, Dict[str, str]],
        target_languages: List[str],
        template_path: Path,
        placeholders_dict: Dict[str, str],
    ) -> None:
        """Generate HTML files for each language with translated text."""
        with open(template_path, "r", encoding="utf-8") as file:
            template_html = file.read()

        for lang in target_languages:
            translated_html = template_html

            # Replace placeholders with translations
            for original_text, placeholder in placeholders_dict.items():
                if lang in translations.get(original_text, {}):
                    translated_text = translations[original_text][lang]
                    translated_html = translated_html.replace(
                        f"{{{{{placeholder}}}}}", translated_text
                    )

            # Save language-specific file
            lang_filename = f"{lang.lower()}_{template_path.name.replace('template_', '')}"
            lang_file_path = self.output_dir / lang_filename

            with open(lang_file_path, "w", encoding="utf-8") as file:
                file.write(translated_html)

            logger.info(f"Generated: {lang_file_path}")

    def generate_redirect_file(self, original_filename: str, target_languages: List[str]) -> None:
        """Generate an HTML file that detects user's language and redirects accordingly."""
        redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Language Selection</title>
    <script>
        function getPreferredLanguage() {{
            const urlParams = new URLSearchParams(window.location.search);
            let lang = urlParams.get('lang') || localStorage.getItem('preferred_language');

            if (!lang) {{
                lang = navigator.language || navigator.userLanguage;
                lang = lang.split('-')[0].toLowerCase();
            }}

            const supportedLangs = {json.dumps([lang.lower() for lang in target_languages])};

            if (!supportedLangs.includes(lang)) {{
                lang = 'english';
            }}

            return lang;
        }}

        const lang = getPreferredLanguage();
        localStorage.setItem('preferred_language', lang);

        // Redirect to language-specific file
        window.location.href = lang + '_{original_filename}';
    </script>
</head>
<body>
    <p>Detecting your language preference...</p>
</body>
</html>"""

        redirect_path = self.output_dir / original_filename
        with open(redirect_path, "w", encoding="utf-8") as file:
            file.write(redirect_html)

        logger.info(f"Generated redirect file: {redirect_path}")

    def process_html_file(self, html_file: Path, target_languages: List[str]) -> None:
        """Process a single HTML file for translation."""
        logger.info(f"Processing: {html_file}")

        # Extract text
        texts = self.extract_text_from_html(html_file)
        if not texts:
            logger.warning(f"No translatable text found in {html_file}")
            return

        # Create placeholders
        placeholders_dict = {text: f"text_{i}" for i, text in enumerate(texts)}

        # Create template
        template_path = self.create_template(html_file, placeholders_dict)

        # Batch translates all texts for efficiency
        translations = {}
        total_texts = len(texts)

        logger.info(f"Translating {total_texts} text blocks into {len(target_languages)} languages")

        for lang_idx, lang in enumerate(target_languages, 1):
            logger.info(f"Translating to {lang} ({lang_idx}/{len(target_languages)})")

            # Create batch context for better translations
            context = f"Website content for a Full Stack Developer portfolio. Translate the following texts to {lang}, maintaining professional tone and technical accuracy:"

            for text_idx, text in enumerate(texts, 1):
                if text_idx % 10 == 0:  # Progress every 10 texts
                    logger.info(f"  Progress: {text_idx}/{total_texts} texts")

                if text not in translations:
                    translations[text] = {}

                translated = self.translate_text_with_context(text, lang, context)
                translations[text][lang] = translated
                # No rate limiting for speed

        # Save translations
        translations_file = self.output_dir / f"{html_file.stem}_translations.json"
        with open(translations_file, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved translations: {translations_file}")

        # Generate language files
        self.generate_language_files(
            translations, target_languages, template_path, placeholders_dict
        )

        # Generate redirect file
        self.generate_redirect_file(html_file.name, target_languages)

    def process_template_directory(self, target_languages: List[str]) -> None:
        """Process all HTML files in the templates directory."""
        if not self.template_dir.exists():
            logger.warning(f"Template directory not found: {self.template_dir}")
            return

        html_files = list(self.template_dir.glob("*.html"))
        if not html_files:
            logger.warning("No HTML files found in templates directory")
            return

        for html_file in html_files:
            try:
                self.process_html_file(html_file, target_languages)
            except Exception as e:
                logger.error(f"Error processing {html_file}: {e}")

    def process_input_directory(self, target_languages: List[str]) -> None:
        """Process all HTML files in the input directory."""
        if not self.input_dir.exists():
            logger.warning(f"Input directory not found: {self.input_dir}")
            return

        html_files = list(self.input_dir.glob("*.html"))
        if not html_files:
            logger.warning("No HTML files found in input directory")
            return

        for html_file in html_files:
            try:
                self.process_html_file(html_file, target_languages)
            except Exception as e:
                logger.error(f"Error processing {html_file}: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Langding - AI-driven landing page auto-translation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        default=settings.INPUT_DIR,
        help="Directory containing input HTML files",
    )

    parser.add_argument(
        "--output-dir", type=str, default=settings.OUTPUT_DIR, help="Directory to save output files"
    )

    parser.add_argument(
        "--template-dir",
        type=str,
        default="templates",
        help="Directory containing template HTML files",
    )

    parser.add_argument(
        "--languages", type=str, nargs="+", help="List of languages to translate into"
    )

    parser.add_argument(
        "--process-templates",
        action="store_true",
        help="Process files from templates directory instead of input directory",
    )

    return parser.parse_args()


def main():
    """Main function to run the translation process."""
    start_time = time.time()

    # Parse arguments
    args = parse_arguments()

    # Validate an API key based on provider
    if settings.AI_PROVIDER.lower() == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")
    else:
        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

    # Set target languages
    target_languages = args.languages if args.languages else settings.LANGS

    logger.info(f"Starting Langding translation process")
    logger.info(f"Target languages: {', '.join(target_languages)}")

    try:
        # Initialize translator
        translator = LangdingTranslator(
            input_dir=args.input_dir, output_dir=args.output_dir, template_dir=args.template_dir
        )

        # Process files
        if args.process_templates:
            logger.info("Processing templates directory")
            translator.process_template_directory(target_languages)
        else:
            logger.info("Processing input directory")
            translator.process_input_directory(target_languages)

        logger.info("Translation process completed successfully")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
