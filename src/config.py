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
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    class Config:
        """
        Config Object.
        """

        env_file = ".env"


settings = Settings()
