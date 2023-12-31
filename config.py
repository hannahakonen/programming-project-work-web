import os
from dotenv import load_dotenv #new, not helping with local config
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env')) #new

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.mailtrap.io') #smtp.googlemail.com
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '2525')) #587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class LocalConfig(Config): #new
    DEBUG = True
    DB_USERNAME = os.environ.get('LOCAL_DB_USERNAME')
    DB_PASSWORD = os.environ.get('LOCAL_DB_PASSWORD')
    DB_SERVER = '192.168.1.35:3306' #TOIMIIIIIIIIIII #'Hannan.localdomain' #'192.168.1.35:3306' #'127.0.0.1:3306' #
    DB_NAME = os.environ.get('LOCAL_DB_NAME')

    
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + '/' + DB_NAME + '?' + 'unix_socket=/run/mysqld/mysqld.sock'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + '/' + DB_NAME + '?' + 'unix_socket=/mnt/c/xampp/mysql/mysql.sock'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_SERVER + '/' + DB_NAME

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'local': LocalConfig,
    'default': DevelopmentConfig
}
