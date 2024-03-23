from flask import render_template,session,request,redirect,url_for,flash,current_app,jsonify,make_response
from shop import db,models

from flask_login import LoginManager, current_user, login_required,login_user, logout_user
from shop.models import User
from shop.decorators import token_required
from .forms import RegistrationForm,LoginForm
from shop.mail import send_email,tokenizationsession,tokenizationconfirmation
from flask_httpauth import HTTPTokenAuth

import jwt
import datetime

import os
from . import admin

from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    # Your token verification logic here
    return True  # Replace with your actual verification logic




@admin.route('/admin')
@auth.login_required
@token_required

def indexpage():
    
   
    if 'email' not in session:
        flash(f"please login first", "danger")
        return redirect(url_for('admin.login'))
    # products=Addproduct.query.all()
    return render_template('admin/index.html',title="Admin Page")


@admin.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        vuser= User.query.filter_by(email=form.email.data).first()
        if not vuser :
            hash_password=generate_password_hash(form.password.data)
            user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                        password=hash_password)
                        
            db.session.add(user)
            name=form.name.data
            flash(f"Welcome {form.name.data}.Thanks for registering.Success")
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account', 'mail/register', user=user, token=token)
            send_email(current_app.config['FLASKY_ADMIN'], ' New User','mail/new_user', user=user)

            return redirect(url_for('admin.indexpage'))

        else:
            flash("User already exists")
            return redirect(url_for('admin.login'))
    return render_template('admin/register.html', form=form,title='Registration Page')

@admin.route('/', methods=['GET', 'POST'])
@auth.login_required
@token_required
def something():
    return redirect(url_for('admin.indexpage'))
    return render_template('admin/index.html')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password,form.password.data):
            login_user(user,form.remember_me.data)
            name=user.name
          
            session['name']=name
            flash(f"Welcome Back {name}.Successful Login")
            email=form.email.data
            # token1=jwt.encode({'user':name,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},current_app.config['SECRET_KEY '])
          
            token=tokenizationsession(name)
            # send_email(current_app.config['FLASKY_ADMIN'], ' New User','mail/new_user', user=user)
            flash(token)
            # tip=token1.decode('UTF-8')
            print(f"?token={token}")
         
        
            return redirect(request.args.get('next') or url_for('admin.indexpage',token=token,_external=True))
        else:
            flash(f" Wrong Password","danger")
              
            return redirect(url_for('admin.login'))
    return render_template('admin/login.html',title='Login Page',form=form,email=session.get('email'))
@admin.route('/confirm/<token>')
@login_required
def confirm(token):
   
    if current_user.confirm(token):
      
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    if current_user.confirmed:
        return redirect(url_for('admin.indexpage'))
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('admin.indexpage'))
@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))  # 

