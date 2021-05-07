import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode('utf-8') or b'secret123456'
    AWS_REGION = 'us-east-1'
    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    USERS_TABLE = 'mysaas-users-dev'
    AUTH_TOKENS_TABLE = 'mysaas-auth-dev'
    EVENT_TABLE = 'mysaas-events-dev'


class ProdConfig(Config):
    USERS_TABLE = 'mysaas-users-prod'
    AUTH_TOKENS_TABLE = 'mysaas-auth-prod'
    EVENT_TABLE = 'mysaas-events-prod'


configs = {
    'local': DevConfig,
    'test': DevConfig,
    'dev': DevConfig,
    'prod': ProdConfig
}


current_config = configs.get(os.environ.get('CONFIG', 'local'))

