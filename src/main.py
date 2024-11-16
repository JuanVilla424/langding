import os
import json
import argparse
import logging
import time
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
import openai
from src.config import settings

# Configure logger
logger = logging.getLogger("__main__")


def configure_logger(log_level: str = "INFO") -> None:
    """
    Configures the logger with rotating file handler and console handler.

    Args:
        log_level (str): Logging level (INFO, DEBUG, etc.).
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logger.setLevel(numeric_level)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        "logs//langding.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    # Console handler
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Langding is an AI driven landing auto-translate site."
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        help="Directory containing input HTML files. Defaults to output folder in current directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save output files. Defaults to output folder in current directory.",
    )
    parser.add_argument(
        "--languages",
        type=str,
        nargs="+",
        default=[],
        help="List of languages to translate into. Defaults to English,Spanish,French,Germany.",
    )
    parser.add_argument(
        "--log-level",
        choices=["INFO", "DEBUG"],
        default="INFO",
        help="Logging level. Defaults to INFO.",
    )
    return parser.parse_args()


def extract_text_from_html(html_file):
    """
    Extract all text content from an HTML file.

    Args:
        html_file (str): Path to the HTML file to parse.

    Returns:
        list: A list of text strings extracted from the HTML file.
    """
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract all text from the HTML, ignoring tags
    texts = [element.strip() for element in soup.stripped_strings]

    return texts


def create_template(html_file, placeholders_dict, output_dir):
    """
    Create a template HTML file where text is replaced by placeholders.

    Args:
        html_file (str): Path to the original HTML file.
        placeholders_dict (dict): Mapping of original text to placeholders.
        output_dir (str): Directory where the template will be saved.

    Returns:
        str: The path to the generated template HTML file.
    """
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Replace text with placeholders
    for text, placeholder in placeholders_dict.items():
        # Find all elements that contain the exact text
        for element in soup.find_all(string=lambda s: s.strip() == text):
            element.replace_with(f"{{{{{placeholder}}}}}")

    # Generate a template file name based on the original file name
    template_filename = os.path.basename(html_file)
    template_path = os.path.join(output_dir, f"template_{template_filename}")

    with open(template_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

    return template_path


def save_translations_to_file(translations, filename):
    """
    Save the translations dictionary to a JSON file.

    Args:
        translations (dict): A dictionary of translated text for each language.
        filename (str): Name of the file to save the translations.
    """
    json_string = json.dumps(translations, ensure_ascii=False, indent=4)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(json_string)


def generate_language_files(
    translations, target_languages, template_path, placeholders_dict, output_dir
):
    """
    Generate HTML files for each language with translated text.

    Args:
        translations (dict): A dictionary containing the translated texts.
        target_languages (list): List of languages to generate HTML for.
        template_path (str): Path to the template HTML file.
        placeholders_dict (dict): Mapping of original text to placeholders.
        output_dir (str): Directory where the output files will be saved.
    """
    with open(template_path, "r", encoding="utf-8") as file:
        template_html = file.read()

    for lang in target_languages:
        translated_html = template_html
        for original_text, placeholder in placeholders_dict.items():
            if lang in translations[original_text]:
                translated_text = translations[original_text][lang]
                # Replace placeholders with translated text
                translated_html = translated_html.replace(f"{{{{{placeholder}}}}}", translated_text)

        # Save the HTML file for the specific language
        lang_filename = os.path.basename(template_path).replace(
            "template_", f"output_{lang.lower()}_"
        )
        lang_file_path = os.path.join(output_dir, lang_filename)
        with open(lang_file_path, "w", encoding="utf-8") as file:
            file.write(translated_html)
        logger.info(f"Generated: {lang_file_path}")


def main():
    """
    Main function to run the translation process for all HTML files in the 'input' directory.
    """
    start_time = time.time()

    args = parse_arguments()
    configure_logger(args.log_level)

    # Directories
    input_dir = settings.INPUT_DIR
    output_dir = settings.OUTPUT_DIR

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # List of languages to translate to (language names)
    target_languages = settings.LANGS

    # Read the OpenAI API key from environment variable
    openai_api_key = settings.OPENAI_API_KEY
    if not openai_api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    # Initialize OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)

    try:
        # Process each HTML file in the input directory
        for filename in os.listdir(input_dir):
            if filename.endswith(".html"):
                html_file = os.path.join(input_dir, filename)
                logger.info(f"Processing file: {html_file}")

                # Step 1: Extract text from the HTML file
                texts = extract_text_from_html(html_file)

                # Skip files with no text
                if not texts:
                    logger.debug(f"No text found in {html_file}. Skipping.")
                    continue

                # Step 2: Create a dictionary to map original text to placeholders
                placeholders_dict = {text: f"placeholder_{i}" for i, text in enumerate(texts)}

                # Step 3: Create the template HTML with placeholders
                template_path = create_template(html_file, placeholders_dict, output_dir)

                # Step 4: Translate extracted texts into multiple languages
                translations = {}
                for text in texts:
                    translations[text] = {}
                    for lang in target_languages:
                        # Create the prompt for translation
                        prompt = f"Translate the following text to {lang}:\n\n{text}"

                        # Call the OpenAI API to get the translation
                        response = client.chat.completions.create(
                            model=settings.OPENAI_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt,
                                }
                            ],
                            temperature=0.3,
                        )

                        # Extract the translated text from the response
                        translated_text = response.choices[0].message.content.strip()
                        translations[text][lang] = translated_text

                # Step 5: Save translations to a file
                translations_filename = os.path.basename(html_file).replace(
                    ".html", "_translations.json"
                )
                translations_path = os.path.join(output_dir, translations_filename)
                save_translations_to_file(translations, translations_path)

                # Step 6: Generate HTML files for each language
                generate_language_files(
                    translations,
                    target_languages,
                    template_path,
                    placeholders_dict,
                    output_dir,
                )

                logger.info("Process Finished")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
    finally:
        end_time = time.time()
        time_elapsed = end_time - start_time
        logger.debug(f"End. Took: {time_elapsed:.4f} seconds")


if __name__ == "__main__":
    main()
