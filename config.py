import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class config():
    def __init__(self):
        pass

    SECRET_KEY = '!@#$%^&*12345678'
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_TEARDOWN = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


    #mail setting
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'cui0xffffff@163.com'
    MAIL_PASSWORD = 'cui123'

    FORUM_MAIL_SUBJECT_PREFIX = 'CUI'
    FORUM_MAIL_SENDER = 'CUI <cui0xffffff@163.com>'

    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DEFAULT_TIME_ZONE = 'CST'

    PER_PAGE = 10
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'nahan/static/upload')
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    MAX_CONTENT_LENGTH = 512*1024

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(config):
    def __init__(self):
        pass
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:cuicui@localhost/nanpan"
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_respository')

class ProductionConfig(config):
    def __init__(self):
        pass

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:cuicui@localhost/nanpan"
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_respository')


config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}