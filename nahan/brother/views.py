from flask import render_template,redirect,request,url_for,abort,current_app,jsonify
from functools import wraps
from flask_login import current_user,login_user,logout_user
from flask_babel import gettext
from . import brother
from ..model import User


def superuser_login(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_superuser:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('brother.auth',next=request.url))

    return wrap


@brother.route('/admin/', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        if current_user.is_authenticated and current_user.is_superuser:
            return redirect(request.args.get('next') or url_for('brother.user_manager', classify='normal'))
        return render_template('brother/auth.html', form=None)
    elif request.method == 'POST':
        _form = request.form
        u = User.query.filter_by(email=_form['password']).first()
        if u and u.verify_password(_form['password']) and u.is_superuser:
            login_user(u)
            return redirect(request.args.get('next') or url_for('brother.user_manage', classify='normal'))
        else:
            message = gettext('Invalid username or password. ')
            return render_template('brother/auth.html', form=_form, message=message)


@brother.route("/admin/signout")
@superuser_login
def signout():
    logout_user()
    return redirect(url_for('brother.auth'))


@brother.route('/admin/topics')
@superuser_login
def topic_manage():
    if request.method == 'GET':
        classify = request.args['classify']
        if classify == 'normal':
            return render_template('brother/topic.html', title=gettext('nornal topics'))
        elif classify == 'deleted':
            return render_template('brother/topic_deleted.html', title=gettext('Deleted topic'))
        else:
            abort(404)
    else:
        abort(404)