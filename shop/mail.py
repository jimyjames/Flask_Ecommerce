from flask_mail import Mail,Message
import jwt
import datetime


from flask import render_template,current_app,request


mail=Mail()
def tokenization(email):
    token=jwt.encode({'user':email,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},current_app.config['SECRET_KEY'])
    return  token 





def send_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
    sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

