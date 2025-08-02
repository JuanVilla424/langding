"""
Unit tests for LangdingTranslator class.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from bs4 import BeautifulSoup

from src.main import LangdingTranslator


class TestLangdingTranslator:
    """Test cases for LangdingTranslator class."""

    @patch("src.main.settings")
    def test_init_openai_provider(self, mock_settings, temp_dir):
        """Test initialization with OpenAI provider."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.ANTHROPIC_API_KEY = None

        with patch("src.main.OpenAI") as mock_openai:
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )
            assert translator.provider == "openai"
            mock_openai.assert_called_once_with(api_key="test-key")

    @patch("src.main.settings")
    def test_init_anthropic_provider(self, mock_settings, temp_dir):
        """Test initialization with Anthropic provider."""
        mock_settings.AI_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        mock_settings.OPENAI_API_KEY = None

        with patch("src.main.Anthropic") as mock_anthropic:
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )
            assert translator.provider == "anthropic"
            mock_anthropic.assert_called_once_with(api_key="test-key")

    @patch("src.main.settings")
    def test_init_missing_api_key(self, mock_settings, temp_dir):
        """Test initialization with missing API key."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None

        with pytest.raises(ValueError, match="OPENAI_API_KEY not set"):
            LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

    @patch("src.main.settings")
    def test_extract_text_from_html(self, mock_settings, temp_dir, sample_html):
        """Test HTML text extraction."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            # Create test HTML file
            html_file = temp_dir / "test.html"
            html_file.write_text(sample_html, encoding="utf-8")

            texts = translator.extract_text_from_html(html_file)

            # Verify extracted texts
            assert "Test Page" in texts
            assert "This is a test page for translation" in texts
            assert "Welcome to Our Website" in texts
            assert "This is the main content paragraph." in texts
            assert len(texts) <= 15  # Limited to 15 texts

    @patch("src.main.settings")
    def test_create_template(self, mock_settings, temp_dir, sample_html):
        """Test template creation."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            # Create test HTML file
            html_file = temp_dir / "test.html"
            html_file.write_text(sample_html, encoding="utf-8")

            placeholders_dict = {
                "Welcome to Our Website": "text_0",
                "This is the main content paragraph.": "text_1",
            }

            template_path = translator.create_template(html_file, placeholders_dict)

            # Verify template was created
            assert template_path.exists()
            assert template_path.name == "template_test.html"

            # Verify placeholders were replaced
            template_content = template_path.read_text(encoding="utf-8")
            assert "{{text_0}}" in template_content
            assert "{{text_1}}" in template_content

    @patch("src.main.settings")
    def test_translate_text_openai(self, mock_settings, temp_dir, mock_openai_response):
        """Test text translation with OpenAI."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"

        with patch("src.main.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai_class.return_value = mock_client

            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            result = translator.translate_text_with_context("Hello", "Spanish", "Test context")

            assert result == "Translated text"
            mock_client.chat.completions.create.assert_called_once()

    @patch("src.main.settings")
    def test_translate_text_anthropic(self, mock_settings, temp_dir, mock_anthropic_response):
        """Test text translation with Anthropic."""
        mock_settings.AI_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        mock_settings.ANTHROPIC_MODEL = "claude-3-haiku-20240307"

        with patch("src.main.Anthropic") as mock_anthropic_class:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_anthropic_response
            mock_anthropic_class.return_value = mock_client

            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            result = translator.translate_text_with_context("Hello", "Spanish", "Test context")

            assert result == "Translated text"
            mock_client.messages.create.assert_called_once()

    @patch("src.main.settings")
    def test_translate_text_error_handling(self, mock_settings, temp_dir):
        """Test error handling in translation."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai_class.return_value = mock_client

            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            result = translator.translate_text_with_context("Hello", "Spanish", "Test context")

            # Should return original text on error
            assert result == "Hello"

    @patch("src.main.settings")
    def test_generate_redirect_file(self, mock_settings, temp_dir):
        """Test redirect file generation."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            translator.generate_redirect_file("index.html", ["Spanish", "French"])

            redirect_file = translator.output_dir / "index.html"
            assert redirect_file.exists()

            content = redirect_file.read_text(encoding="utf-8")
            assert "window.location.href" in content
            assert "spanish" in content.lower()
            assert "french" in content.lower()

    @patch("src.main.settings")
    def test_generate_language_files(self, mock_settings, temp_dir, sample_translations):
        """Test language-specific file generation."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"), output_dir=str(temp_dir / "output")
            )

            # Create template file
            template_content = """
            <html>
                <body>
                    <h1>{{text_0}}</h1>
                    <p>{{text_1}}</p>
                </body>
            </html>
            """
            template_path = translator.output_dir / "template_test.html"
            template_path.write_text(template_content, encoding="utf-8")

            placeholders_dict = {
                "Welcome to Our Website": "text_0",
                "This is the main content paragraph.": "text_1",
            }

            translator.generate_language_files(
                sample_translations, ["Spanish", "French"], template_path, placeholders_dict
            )

            # Verify language files were created
            spanish_file = translator.output_dir / "spanish_test.html"
            french_file = translator.output_dir / "french_test.html"

            assert spanish_file.exists()
            assert french_file.exists()

            # Verify content was translated
            spanish_content = spanish_file.read_text(encoding="utf-8")
            assert "Bienvenido a Nuestro Sitio Web" in spanish_content
            assert "Este es el párrafo de contenido principal." in spanish_content
