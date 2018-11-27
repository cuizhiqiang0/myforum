from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config


app = Flask(__name__)
mail = Mail()


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

app.config.from_object(config['default'])
config['default'].init_app(app)

mail.init_app(app)

db = SQLAlchemy(app)
db.init_app(app)

login_manager.init_app(app)

'''
数据库升降版本的方式
python manage.py db init
python manage.py db migrate --message ' ha'
python manage.py db upgrade
回退,先看版本号
#建议先使用python database.py db history命令查看历史版本的具体版本号，然后复制具体版本号执行回退。
python manager.py db downgrade 版本号
'''
#blueprint
from .user import user as user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')
from .voice import voice as voice_blueprint
app.register_blueprint(voice_blueprint)
from .brother import brother as brother_blueprint
app.register_blueprint(brother_blueprint)