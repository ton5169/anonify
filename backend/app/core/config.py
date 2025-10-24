from starlette.config import Config

config = Config(".env")

PROJECT_NAME = "Anonify"
VERSION = "1.0.0"
API_PREFIX = "/api/v1"


AUTH_PASSWORD = config("AUTH_PASSWORD", cast=str, default="ChangeMe123!")
