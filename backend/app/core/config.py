import os
from starlette.config import Config

from dotenv import load_dotenv

env_file_path = os.getenv("ENV_FILE", ".env")
load_dotenv(env_file_path, override=False)

config = Config(env_file_path)

PROJECT_NAME = "Anonify"
VERSION = "1.0.0"
API_PREFIX = "/api/v1"


AUTH_PASSWORD = config("AUTH_PASSWORD", cast=str, default="ChangeMe123!")
MAX_TEXT_LENGTH = config("MAX_TEXT_LENGTH", cast=int, default=5000)
HF_TOKEN = config("HF_TOKEN", cast=str, default="test_token")
