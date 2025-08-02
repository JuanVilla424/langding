"""
Pytest configuration and fixtures for Langding tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Test Page</title>
        <meta name="description" content="This is a test page for translation">
    </head>
    <body>
        <h1>Welcome to Our Website</h1>
        <p>This is the main content paragraph.</p>
        <p>Here is another paragraph with more content.</p>
        <div>
            <h2>Section Title</h2>
            <p>Section content goes here.</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Translated text"
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "Translated text"
    return mock_response


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return {
        "AI_PROVIDER": "openai",
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key",
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "ANTHROPIC_MODEL": "claude-3-haiku-20240307",
        "OUTPUT_DIR": "test_output",
        "INPUT_DIR": "test_input",
        "LANGS": ["English", "Spanish", "French"],
    }


@pytest.fixture
def sample_translations():
    """Sample translation data."""
    return {
        "Welcome to Our Website": {
            "Spanish": "Bienvenido a Nuestro Sitio Web",
            "French": "Bienvenue sur Notre Site Web",
        },
        "This is the main content paragraph.": {
            "Spanish": "Este es el párrafo de contenido principal.",
            "French": "Ceci est le paragraphe de contenu principal.",
        },
    }
