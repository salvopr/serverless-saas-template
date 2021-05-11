import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode('utf-8') or b'secret123456'
    AWS_REGION = 'us-east-1'
    STRIPE_PUB_KEY = os.environ.get('STRIPE_PUB_KEY')
    STRIPE_SEC_KEY = os.environ.get('STRIPE_SEC_KEY')
    STRIPE_ENDPOINT_KEY = os.environ.get('STRIPE_ENDPOINT_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    USERS_TABLE = 'mysaas-users-dev'
    AUTH_TOKENS_TABLE = 'mysaas-auth-dev'
    EVENT_TABLE = 'mysaas-events-dev'
    DOMAIN = "mysaas.com"  # no http prefix


class ProdConfig(Config):
    USERS_TABLE = 'mysaas-users-prod'
    AUTH_TOKENS_TABLE = 'mysaas-auth-prod'
    EVENT_TABLE = 'mysaas-events-prod'
    DOMAIN = "mysaas.com"  # no http prefix


configs = {
    'local': DevConfig,
    'test': DevConfig,
    'dev': DevConfig,
    'prod': ProdConfig
}


current_config = configs.get(os.environ.get('CONFIG', 'local'))

