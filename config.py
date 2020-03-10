import os


class Config(object):
    DEBUG = False
    TESTING = False
    TRACK_MODIFICATIONS = True
    SECRET_KEY = 'changeit'
    UPLOAD_FOLDER = 'static'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://eform:changeit@wzhzzmzzy.xyz:5432/eform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 5


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://eform:changeit@wzhzzmzzy.xyz:5432/eform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    'DEVELOP': DevelopmentConfig,
    'PRODUCT': ProductionConfig,
    'TESTING': TestingConfig
}
