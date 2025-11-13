from .base_config import BaseConfig

class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
