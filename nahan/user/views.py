from flask import render_template,redirect,request,url_for,abort,current_app
from flask_login import logout_user,login_user,login_required,current_user
from flask_babel import gettext
from flask_paginate import Pagination
import re
import os
from PIL import Image
from datetime import datetime
from . import user
from ..model import User
from .. import db
from ..email import send_email


alphanumeric = re.compile(r'^[0-9a-zA-Z\_]*$')
email_address = re.compile(r'[a-zA-z0-9]+\@[a-zA-Z0-9]+\.+[a-zA-Z]')

@user.route('/signin', methods=['GET', 'POST'])
def signin():
    print(request.method)
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(request.args.get('next')) or url_for('voice.index')
        return render_template('user/signin.html', title=gettext('user sign in '), form=None)
    elif request.method == 'POST':
        _form = request.form
        print(_form['email'])
        print(_form['password'])
        u = User.query.filter_by(email=_form['email']).first()
        if u and u.verify_password(_form['password']):
            login_user(u)
            u.last_login = datetime.now()
            db.session.commit()
            return redirect(request.args.get('next') or url_for('voice.index'))
        else:
            message = gettext('Invalid username or password')
            return render_template('/user/signin.html', title=gettext('user sign in'), form = _form, message=message)

@user.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('voice.index'))

@user.route('/register', methods=['GET', 'POST'])
def reg():
    print(request.method)
    if request.method == 'GET':
        return render_template('user/reg.html', title=gettext('register a account'), form=None)
    elif request.method == 'POST':
        _form = request.form
        username = _form['username']
        email = _form['email']
        password = _form['password']
        password2 = _form['password2']

        message_e, message_u, message_p = '','',''

        # Check username is valid or not.
        if not username:
            message_u = gettext('username cannot be empty')
        elif not alphanumeric.match(username):
            message_u = gettext('Username can only contain letters digits and underscore.')
        elif User.query.filter_by(username=username).first():
            message_u = gettext('Username already exists.')

        # Check email is valid or not.
        if not email:
            message_e = gettext('Email address can not be empty.')
        elif not email_address.match(email):
            message_e = gettext('Email address is invalid.')
        elif User.query.filter_by(email=email).first():
            message_e = gettext('Email already exists.')

        # Check the password is valid or not.
        if password != password2:
            message_p = gettext("Passwords don't match.")
        elif password == "" or password2 == "":
            message_p = gettext("Passwords can not be empty.")

        if message_u or message_p or message_e:
            return render_template("user/reg.html", form=_form,
                                   title=gettext('register a account'),
                                   message_u=message_u,
                                   message_p=message_p,
                                   message_e=message_e)
        else:
            reg_user = User(username=username, email=email,password=password)
            # TODO, Confirm the email.
            #token = reg_user.generate_reset_token()
            #send_email(reg_user.email, 'confirm your account','user/registerConfirm', user=reg_user, token=token)


            db.session.add(reg_user)
            db.session.commit()

            return redirect(url_for('user.signin'))


@user.route('/<int:uid>')
def info(uid):
    u = User.query.filter_by(uid=uid, deleted=False).first_or_404()

    per_page = current_app.config['PER_PAGE']
    page = request.args.get('page', 1)
    offset = (page - 1) * per_page
    a = u.extract_topics()

    topic_all = list(filter(lambda x: not x.deleted, u.extract_topics()))
    topic_all.sort(key=lambda t: (t.reply_count, t.click), reverse=True)
    topics = topic_all[offset:offset+per_page]
    pagination = Pagination(page=page,total=len(topic_all),
                                per_page=per_page,
                            record_name='topics',
                            CSS_FRAMEWORK='bootstrap',
                            bs_version=3)
    return render_template('user/info.html', topics=topics,
                           title=u.username + gettext("'s topics"),
                           post_list_title = u.username + gettext("'s topics"),
                           pagination=pagination,
                           user=u)


@user.route('/setting/info', methods=['GET', 'POST'])
@login_required
def setting_info():
    if request.method == 'GET':
        return render_template('user/setting_info.html', form=None)
    elif request.method == 'POST':
        _form = request.form
        email_addr = _form['email']
        web_addr = _form['website']

        message_email = ""
        if not email_addr:
            message_email = gettext('enail address can not be empty')
        elif not email_address.match(email_addr):
            message_email = gettext('email address is invalid')

        #TODO
        if message_email:
            return render_template("user/setting_info.html", message_email=message_email)
        else:
            current_user.website = web_addr
            current_user.email = email_addr
            db.session.commit()
            message_success = gettext('Update info done!')
            return render_template('user/setting_info.html', message_success=message_success)


@user.route('/password/reset', methods=['GET', 'POST'])
def password_reset_request():
    pass


@user.route('/notify')
@login_required
def notify():
    if request.method == 'GET':
        new = current_user.extract_unread_notify()
        old = current_user.extract_read_notify()

        if current_user.unread_notify:
            if current_user.read_notify:
                current_user.read_notify = "%s,%s" % \
                    (current_user.unread_notify, current_user.read_notify)
            else:
                current_user.read_notify = current_user.unread_notify

        current_user.unread_notify = ''
        db.session.commit()

        return render_template('user/notify.html', title=gettext('Notify'), old=old, new=new)
    else:
        abort(404)


@user.route("/setting/password", methods=['GET', 'POST'])
@login_required
def setting_password():
    if request.method == 'GET':
        return render_template('user/setting_passwd.html', form=None)
    elif request.method == 'POST':
        _form = request.form
        cur_password = _form['old_password']
        new_password = _form['password']
        new_password2 = _form['password2']

        message_cur, message = '',''
        if not cur_password:
            message_cur = "The old password can not be empty."
        elif not current_user.verify_password(cur_password):
            message_cur = "The old password is not correct."

        if new_password != new_password2:
            message_new = gettext("Passwords don't match.")
        elif new_password2 == "" or new_password == "":
            message_new = gettext("Passwords can not be empty.")

        if message_cur or message_new:
            return render_template("user/setting_passwd.html", form=_form,
                                   message_cur=message_cur,
                                   message_new=message_new)
        else:
            current_user.password = new_password
            db.session.commit()
            message_success = gettext("Update password done!")
            return render_template("user/setting_passwd.html",
                                   message_success=message_success)


@user.route('/setting/avator', methods=['GET', 'POST'])
@login_required
def setting_avatar():
    if request.method == 'GET':
        return render_template('user/setting_avatar.html', form=None)
    elif request.method == 'POST':
        _file = request.files['file']
        if not _file or _file.filename == '':
            message_fail = gettext('No selected file')
            return render_template('user/setting_avatar.html', message_fail=message_fail)

        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if '.' in _file.filename:
            file_appendix = _file.filename.rsplit('.', 1)[1]

        if _file and '.' in _file.filename and file_appendix in allowed_extensions:
            im = Image.open(_file)
            im.thumbnail((128,128), Image.ANTIALIAS)
            im.save("%s/%d.png" % (upload_folder, current_user.uid), 'PNG')

            image_path = os.path.join(upload_folder, '%d.png'%current_user.uid)
            unique_mark = os.stat(image_path).st_mtime
            print('hahahahaa')
            current_user.avatar_url = url_for('static', filename='upload/%d.png'%current_user.uid, t=unique_mark)
            db.session.commit()
            message_success = gettext('Update avatar done')
            return render_template('user/setting_avatar.html', message_success=message_success)
        else:
            message_fail = gettext('Invalid file')
            return render_template('user/setting_avatar.html', message_fail=message_fail)

@user.app_errorhandler(404)
def voice_404(err):
    return render_template('404.html'), 404


@user.app_errorhandler(403)
def voice_403(err):
    return render_template('403.html'), 403


@user.app_errorhandler(500)
def voice_500(err):
    return render_template('500.html'), 500