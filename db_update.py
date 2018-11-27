from migrate.versioning import api
#from config import SQLALCHEMY_MIGRATE_REPO
#from config import SQLALCHEMY_DATABASE_URI
from config import DevelopmentConfig

api.upgrade(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
ver = api.db_version(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
print('Current version:' + str(ver))