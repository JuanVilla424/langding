"""
Integration tests for Langding main functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.main import main, parse_arguments, LangdingTranslator


class TestIntegration:
    """Integration test cases for Langding application."""

    def test_parse_arguments_default(self):
        """Test argument parsing with default values."""
        with patch("sys.argv", ["langding.py"]):
            args = parse_arguments()
            assert args.input_dir == "input"
            assert args.output_dir == "output"
            assert args.template_dir == "templates"
            assert args.languages is None
            assert args.process_templates is False

    def test_parse_arguments_custom(self):
        """Test argument parsing with custom values."""
        test_args = [
            "langding.py",
            "--input-dir",
            "custom_input",
            "--output-dir",
            "custom_output",
            "--template-dir",
            "custom_templates",
            "--languages",
            "Spanish",
            "French",
            "--process-templates",
        ]

        with patch("sys.argv", test_args):
            args = parse_arguments()
            assert args.input_dir == "custom_input"
            assert args.output_dir == "custom_output"
            assert args.template_dir == "custom_templates"
            assert args.languages == ["Spanish", "French"]
            assert args.process_templates is True

    @patch("src.main.settings")
    def test_full_translation_workflow(self, mock_settings, temp_dir, sample_html):
        """Test complete translation workflow."""
        # Setup mock settings
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"
        mock_settings.LANGS = ["English", "Spanish", "French"]

        # Create test directories
        input_dir = temp_dir / "input"
        output_dir = temp_dir / "output"
        template_dir = temp_dir / "templates"

        input_dir.mkdir()
        output_dir.mkdir()
        template_dir.mkdir()

        # Create test HTML file
        html_file = template_dir / "index.html"
        html_file.write_text(sample_html, encoding="utf-8")

        # Mock OpenAI responses
        mock_responses = {
            "Spanish": "Texto traducido al español",
            "French": "Texte traduit en français",
        }

        def mock_translate_side_effect(text, target_lang, context):
            if target_lang in mock_responses:
                return mock_responses[target_lang]
            return text

        with patch("src.main.OpenAI") as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client

            translator = LangdingTranslator(
                input_dir=str(input_dir), output_dir=str(output_dir), template_dir=str(template_dir)
            )

            # Mock the translation method
            translator.translate_text_with_context = Mock(side_effect=mock_translate_side_effect)

            # Process the HTML file
            translator.process_template_directory(["Spanish", "French"])

            # Verify outputs were created
            assert (output_dir / "template_index.html").exists()
            assert (output_dir / "spanish_index.html").exists()
            assert (output_dir / "french_index.html").exists()
            assert (output_dir / "index.html").exists()  # Redirect file
            assert (output_dir / "index_translations.json").exists()

            # Verify translations JSON
            translations_file = output_dir / "index_translations.json"
            with open(translations_file, "r", encoding="utf-8") as f:
                translations = json.load(f)

            assert isinstance(translations, dict)
            assert len(translations) > 0

    @patch("src.main.settings")
    def test_process_nonexistent_directory(self, mock_settings, temp_dir):
        """Test processing non-existent directory."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "nonexistent"), output_dir=str(temp_dir / "output")
            )

            # Should handle gracefully
            translator.process_input_directory(["Spanish"])

    @patch("src.main.settings")
    def test_empty_html_processing(self, mock_settings, temp_dir):
        """Test processing HTML with no translatable content."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        # Create empty HTML
        empty_html = "<html><head></head><body></body></html>"

        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        html_file = template_dir / "empty.html"
        html_file.write_text(empty_html, encoding="utf-8")

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"),
                output_dir=str(temp_dir / "output"),
                template_dir=str(template_dir),
            )

            # Should handle gracefully
            translator.process_template_directory(["Spanish"])

    @patch("src.main.settings")
    def test_main_function_openai(self, mock_settings):
        """Test main function with OpenAI provider."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.ANTHROPIC_API_KEY = None
        mock_settings.LANGS = ["Spanish", "French"]

        test_args = ["langding.py", "--process-templates"]

        with (
            patch("sys.argv", test_args),
            patch("src.main.OpenAI"),
            patch("src.main.LangdingTranslator") as mock_translator_class,
        ):

            mock_translator = Mock()
            mock_translator_class.return_value = mock_translator

            main()

            # Verify translator was created and used
            mock_translator_class.assert_called_once()
            mock_translator.process_template_directory.assert_called_once_with(
                ["Spanish", "French"]
            )

    @patch("src.main.settings")
    def test_main_function_anthropic(self, mock_settings):
        """Test main function with Anthropic provider."""
        mock_settings.AI_PROVIDER = "anthropic"
        mock_settings.ANTHROPIC_API_KEY = "test-key"
        mock_settings.OPENAI_API_KEY = None
        mock_settings.LANGS = ["Spanish", "French"]

        test_args = ["langding.py", "--input-dir", "test_input", "--output-dir", "test_output"]

        with (
            patch("sys.argv", test_args),
            patch("src.main.Anthropic"),
            patch("src.main.LangdingTranslator") as mock_translator_class,
        ):

            mock_translator = Mock()
            mock_translator_class.return_value = mock_translator

            main()

            # Verify translator was created and used
            mock_translator_class.assert_called_once()
            mock_translator.process_input_directory.assert_called_once_with(["Spanish", "French"])

    @patch("src.main.settings")
    def test_main_function_missing_api_key(self, mock_settings):
        """Test main function with missing API key."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None

        test_args = ["langding.py"]

        with patch("sys.argv", test_args):
            with pytest.raises(ValueError, match="Please set the OPENAI_API_KEY"):
                main()

    @patch("src.main.settings")
    def test_main_function_custom_languages(self, mock_settings):
        """Test main function with custom languages."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.LANGS = ["English", "Spanish"]

        test_args = [
            "langding.py",
            "--languages",
            "German",
            "Italian",
            "Portuguese",
            "--process-templates",
        ]

        with (
            patch("sys.argv", test_args),
            patch("src.main.OpenAI"),
            patch("src.main.LangdingTranslator") as mock_translator_class,
        ):

            mock_translator = Mock()
            mock_translator_class.return_value = mock_translator

            main()

            # Verify custom languages were used
            mock_translator.process_template_directory.assert_called_once_with(
                ["German", "Italian", "Portuguese"]
            )

    @patch("src.main.settings")
    def test_error_handling_in_translation(self, mock_settings, temp_dir):
        """Test error handling during translation process."""
        mock_settings.AI_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"

        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        # Create invalid HTML file
        html_file = template_dir / "invalid.html"
        html_file.write_text("Invalid HTML content", encoding="utf-8")

        with patch("src.main.OpenAI"):
            translator = LangdingTranslator(
                input_dir=str(temp_dir / "input"),
                output_dir=str(temp_dir / "output"),
                template_dir=str(template_dir),
            )

            # Should handle errors gracefully
            translator.process_template_directory(["Spanish"])
