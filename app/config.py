import os

class Settings:
    APP_NAME = "Oceanicmach"
    APP_VERSION = "0.1.0"
    TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
    STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

settings = Settings()
