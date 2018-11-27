import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_babel import Babel
from nahan import app,db

manager = Manager(app)
migrate = Migrate(app, db)
babel = Babel(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    #python3 manager.py runserver --host 0.0.0.0 --port 9800
    #manager.run()
