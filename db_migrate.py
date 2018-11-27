import  imp
from migrate.versioning import api
from nahan import db
#from config import SQLALCHEMY_MIGRATE_REPO,SQLALCHEMY_DATABASE_URI
from config import DevelopmentConfig

ver = api.db_version(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
migration = DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (ver + 1))
tmp_module = imp.new_module('old_model')
old_module = api.create_model(DevelopmentConfig.SQLALCHEMY_DATABASE_URI, DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
exec(old_module,tmp_module.__dict__)
script = api.make_update_script_for_model(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,
            DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)

api.upgrade(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
ver = api.db_version(DevelopmentConfig.SQLALCHEMY_DATABASE_URI,DevelopmentConfig.SQLALCHEMY_MIGRATE_REPO)
print('New migration saved as' + migration)
print('Current databse version:' + str(ver))