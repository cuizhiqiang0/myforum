from migrate.versioning import api
#from config import SQLALCHEMY_MIGRATE_REPO,SQLALCHEMY_DATABASE_URI
from config import DevelopmentConfig

ver = api.db_version(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
if ver > 0:
    api.downgrade(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO, ver-1)
ver = api.db_version(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
print('Currntt databse version: ' + str(ver))