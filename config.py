import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode('utf-8') or b'secret123456'
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    STRIPE_PUB_KEY = os.environ.get('STRIPE_PUB_KEY')
    STRIPE_SEC_KEY = os.environ.get('STRIPE_SEC_KEY')
    STRIPE_ENDPOINT_KEY = os.environ.get('STRIPE_ENDPOINT_KEY')

    @staticmethod
    def init_app(app):
        pass


class LocalConfig(Config):
    USERS_TABLE = os.environ.get('USERS_TABLE', 'mysaas-users-dev')
    AUTH_TOKENS_TABLE = os.environ.get('AUTH_TOKENS_TABLE', 'mysaas-auth-dev')
    EVENT_TABLE = os.environ.get('EVENT_TABLE', 'mysaas-events-dev')
    DOMAIN = os.environ.get('DOMAIN', "mysaas.com")  # no http prefix and trailing slash


class TestConfig(Config):
    USERS_TABLE = os.environ.get('USERS_TABLE', 'mysaas-users-dev')
    AUTH_TOKENS_TABLE = os.environ.get('AUTH_TOKENS_TABLE', 'mysaas-auth-dev')
    EVENT_TABLE = os.environ.get('EVENT_TABLE', 'mysaas-events-dev')
    DOMAIN = os.environ.get('DOMAIN', "mysaas.com")  # no http prefix and trailing slash


class ProdConfig(Config):
    USERS_TABLE = os.environ.get('USERS_TABLE', 'mysaas-users-prod')
    AUTH_TOKENS_TABLE = os.environ.get('AUTH_TOKENS_TABLE', 'mysaas-tokens-prod')
    EVENT_TABLE = os.environ.get('EVENT_TABLE', 'mysaas-events-prod')
    DOMAIN = os.environ.get('DOMAIN', "mysaas.com")  # no http prefix and trailing slash


configs = {
    'local': LocalConfig,
    'test': TestConfig,
    'dev': LocalConfig,
    'prod': ProdConfig
}


current_config = configs.get(os.environ.get('CONFIG', 'local'))

