from flask_mail import Mail,Message
import jwt
import datetime
from threading import Thread
from . import mail

from flask import render_template,current_app,request



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)



def tokenizationconfirmation (name):
    token=jwt.encode({'user':name,'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=90)},current_app.config['SECRET_KEY'])
    return  token 
def tokenizationsession (name):
    token=jwt.encode({'user':name,'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=72)},current_app.config['SECRET_KEY'])
    return  token 





def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs) 
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
   

