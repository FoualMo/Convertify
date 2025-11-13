from .base_config import BaseConfig

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"
