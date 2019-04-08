import os


class Config(object):
    DEBUG = False
    TESTING = False
    TRACK_MODIFICATIONS = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    'DEVELOP': DevelopmentConfig,
    'PRODUCT': ProductionConfig,
    'TESTING': TestingConfig
}