from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,validators,Form
from wtforms.validators import DataRequired, Length, Email

class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
    
  
