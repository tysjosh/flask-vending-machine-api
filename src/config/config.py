"""Flask configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:

    # SECRET_KEY = os.environ.get("SECRET_KEY")
    # JWT_SECRET_KEY= os.environ.get("JWT_SECRET_KEY")
    SECRET_KEY='my-secret-key'
    JWT_SECRET_KEY='my-jwt-secret-key'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SWAGGER={
                'title': "Vending Machine API",
                'uiversion': 3
            }


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS=False


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

 
config_dict={
    'dev':DevConfig,
    'testing':TestConfig,
    'production':ProdConfig
}