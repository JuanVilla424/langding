# src/config.py
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings Object.

    Args:
        :param BaseSettings: (BaseSettings) Base Settings Object.
    """

    # Global Config (Optional)
    INPUT_DIR: str = "input"
    OUTPUT_DIR: str = "output"
    LANGS: list = ["English", "Spanish", "French", "German"]

    # API Keys (only one required)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")

    # Model selection
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # "openai" or "anthropic"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    class Config:
        """
        Config Object.
        """

        env_file = ".env"


settings = Settings()
