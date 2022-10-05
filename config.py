import os
import datetime

class Config(object):
    DEBUG = False
    TESTING = False
    # DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    # DATABASE_URI = 'mysql://user@localhost/foo'
    # Server uri where images of riskradar are put e.g.: 'http://localhost/images/risk/'
    SERVER_URI = <PRODUCTION_SERVER_URI>
    SECRET_KEY = <PRODUCTION_SECRET_KEY>
    JWT_SECRET_KEY = <PRODUCTION_JWT_SECRET_KEY>
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    MONGO_SERVER = <PRODUCTION_MONGO_SERVER_IP>
    MONGO_PORT = <PRODUCTION_MONGO_PORT>
    MONGO_USERNAME = <PRODUCTION_MONGO_USERNAME>
    MONGO_PASSWORD = <PRODUCTION_MONGO_PASSWORD>
    MONGO_AUTH_SOURCE = <PRODUCTION_MONGO_AUTH_SOURCE>
    TOKEN = <RANDOM_NUMBER>  # e.g. 1234567890

class DevelopmentConfig(Config):
    DEBUG = True
    # Server uri where images of riskradar are put e.g.: 'http://localhost/images/risk/'
    SERVER_URI = <DEVELOPMENT_SERVER_URI>
    SECRET_KEY = <DEVELOPMENT_SECRET_KEY>
    JWT_SECRET_KEY = <DEVELOPMENT_JWT_SECRET_KEY>
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    MONGO_SERVER = <DEVELOPMENT_MONGO_SERVER_IP>
    MONGO_PORT = <DEVELOPMENT_MONGO_PORT>
    MONGO_USERNAME = <DEVELOPMENT_MONGO_USERNAME>
    MONGO_PASSWORD = <DEVELOPMENT_MONGO_PASSWORD>
    MONGO_AUTH_SOURCE = <DEVELOPMENT_MONGO_AUTH_SOURCE>
    TOKEN = <RANDOM_NUMBER>  # e.g. 1234567890

class TestingConfig(Config):
    TESTING = True
    # Server uri where images of riskradar are put e.g.: 'http://localhost/images/risk/'
    SERVER_URI = <TESTING_SERVER_URI>
    SECRET_KEY = <TESTING_SECRET_KEY>
    JWT_SECRET_KEY = <TESTING_JWT_SECRET_KEY>
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    MONGO_SERVER = <TESTING_MONGO_SERVER_IP>
    MONGO_PORT = <TESTING_MONGO_PORT>
    MONGO_USERNAME = <TESTING_MONGO_USERNAME>
    MONGO_PASSWORD = <TESTING_MONGO_PASSWORD>
    MONGO_AUTH_SOURCE = <TESTING_MONGO_AUTH_SOURCE>
    TOKEN = <RANDOM_NUMBER>  # e.g. 1234567890
