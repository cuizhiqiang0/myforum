from migrate.versioning import api
#from config import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_MIGRATE_REPO,SQLALCHEMY_TRACK_MODIFICATIONS
from config import DevelopmentConfig
from nahan import db
import os.path
db.create_all()

if not os.path.exists(DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO):
    api.create(DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO, 'db_repository')
    api.version_control(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO,api.version(DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO))
