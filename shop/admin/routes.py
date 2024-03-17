from flask import render_template,session,request,redirect,url_for,flash
from shop import app,db,models
from shop.models import User
from .forms import RegistrationForm,LoginForm
import os
from werkzeug.security import check_password_hash, generate_password_hash


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f"please login first", "danger")
        return redirect(url_for('login'))
    # products=Addproduct.query.all()
    return render_template('admin/index.html',title="Admin Page")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password=generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        flash(f"Welcome {form.name.data}.Thanks for registering.Success")
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('admin/register.html', form=form,title='Registration Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password,form.password.data):
            session['email']=form.email.data
            flash(f"Welcome Back {form.email.data}.Successful Login")
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash(f" Wrong Password","danger")
              
            return redirect(url_for('login'))
    return render_template('admin/login.html',title='Login Page',form=form)

