import os

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
  """
  Application configuration settings.
  """
  # Project metadata
  PROJECT_NAME: str = "Document Processing API"
  VERSION: str = "1.0.0"
  API_V1_STR: str = "/api/v1"

  # Secret key for signing tokens or sensitive data
  SECRET_KEY: str = "Secret key"

  # Token expiration time (in minutes), default is 8 days
  ACESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

  # Static folder configuration
  WEB_FOLDER: str = "www"  # Path to the static web folder

  # Database configuration
  DATABASE_URL: str = "sqlite:///./sql_app.db"  # Database connection URL

  # CORS (Cross-Origin Resource Sharing) settings
  BACKEND_CORS_ORIGINS: list = ["*"]  # Allowed origins for CORS requests

  # Directory for uploaded files
  UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

  # Maximum file size for uploads (10MB)
  MAX_FILE_SIZE: int = 10 * 1024 * 1024

  # Allowed file extensions for uploads
  ALLOWED_EXTENSIONS: set = {"pdf", "docx", "pptx", "xlsx", "csv", "txt"}

  class Config:
    case_sensitive = True  # Enforce case sensitivity for environment variables
    env_file = ".env"  # Path to the environment file
    env_file_encoding = "utf-8"  # Encoding for the environment file

settings = Settings()