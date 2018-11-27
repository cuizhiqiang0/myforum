from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail

def send_async_mail(_app, msg):
    with _app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FORUM_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
            sender=app.config['FORUM_MAIL_SENDER'],recipients=[to, app.config['MAIL_USERNAME']])

    msg.html = render_template(template + '.html' ,**kwargs)
    print(msg.html)
    thread1 = Thread(target=send_async_mail, args=[app, msg])
    thread1.start()

    return thread1
