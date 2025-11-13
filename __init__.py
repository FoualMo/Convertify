import os
from .dev_config import DevelopmentConfig
from .prod_config import ProductionConfig
from .site_config import SiteConfig

def get_config():
    env = os.getenv("FLASK_ENV", "development")

    # Cherche la config principale
    base_config = ProductionConfig if env == "production" else DevelopmentConfig

    # Crée dynamiquement une classe fusionnant les deux
    class CombinedConfig(base_config, SiteConfig):
        pass

    return CombinedConfig
