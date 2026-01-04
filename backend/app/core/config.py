from starlette.config import Config

config = Config(".env")

PROJECT_NAME = "Anonify"
VERSION = "1.0.0"
API_PREFIX = "/api/v1"


AUTH_PASSWORD = config("AUTH_PASSWORD", cast=str, default="ChangeMe123!")
MAX_TEXT_LENGTH = config("MAX_TEXT_LENGTH", cast=int, default=5000)
HF_TOKEN = config("HF_TOKEN", cast=str, default="test_token")
