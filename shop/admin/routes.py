from flask import render_template,session,request,redirect,url_for,flash,current_app,jsonify,make_response
from shop import db,models
from flask_pydantic import validate

from flask_login import LoginManager, current_user, login_required,login_user, logout_user
from shop.models import User,Product,ProductDescription,Order
from shop.decorators import token_required
from .forms import RegistrationForm,LoginForm
from shop.mail import send_email,tokenizationsession,tokenizationconfirmation
from flask_httpauth import HTTPTokenAuth
from ..schemas import Productin,Productout,ProductDescriptionin,Productdescriptionout,Userin,Userout,Userdetails,Orderin,Orderout,Testlogin
from typing import List

import jwt
import datetime
from datetime import datetime,timedelta
from pydantic import ValidationError

import os
from . import admin

from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    # Your token verification logic here
    return True  # Replace with your actual verification logic
# 



@admin.route('/admin')
@auth.login_required
@token_required

def indexpage():
    
   
    if 'email' not in session:
        flash(f"please login first", "danger")
        return redirect(url_for('admin.login'))
    print(session)
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
        
          
            token=tokenizationsession(name)
           
            print(f"?token={token}")
         
        
            return redirect(request.args.get('next') or url_for('admin.indexpage',token=token,_external=True))
        else:
            flash(f" Wrong Password","danger")
              
            return redirect(url_for('admin.login'))
    return render_template('admin/login.html',title='Login Page',form=form,email=session.get('email'))
@admin.route('/confirm/<token>')
def confirm(token):
    print(current_user.confirm(token))
    
    
   
    if current_user.confirmed:
        return redirect(url_for('admin.indexpage',token=token,_external=True))
    elif current_user.confirm(token):
        
      
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('admin.indexpage'))
@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))  # 



@admin.route('/products',methods=['POST'])
@validate()
def addproduct(body:Productin):
    if request.method=='POST':
        new_product = Product(
            category=body.category,
            name=body.name,
            description=body.description,
            price=body.price
        )
        db.session.add(new_product)
        db.session.commit()
        id=new_product.id
        for detail in body.detail:
             new_productdesc = ProductDescription(product_id=id, title=detail.title, description=detail.description)
             db.session.add(new_productdesc)
        db.session.commit()
        response=Productout.from_orm(new_product)
        return response.dict()

@admin.route('/products/<int:id>')
def view_product(id: int):
    if request.method =="GET":
        product = Product.query.get_or_404(id)

        response = Productout.from_orm(product)
        return response.dict()
    


@admin.route('/products')
@login_required
def view_product_all():
    if request.method=='GET':
        product = Product.query.all()

        response_list = []
        for prod in product:
            response_list.append(Productout.from_orm(prod).dict())

        return response_list


@admin.route('/products/detail',methods=['POST','GET'])
@validate()
def addproductdetail(body:ProductDescriptionin):
    new=ProductDescription(**body.dict())
    db.session.add(new)
    db.session.commit()
    response=Productdescriptionout.from_orm(new)
    return response.dict()


@admin.route('/products/<int:id>', methods=['PUT'])
@validate()
def edit_product(id: int, body: Productin):
    if request.method == 'PUT':
        product = Product.query.get_or_404(id)
        product.name = body.name
        product.category = body.category
        product.description = body.description
        product.price = body.price
        for detail in body.detail:
            productdesc = ProductDescription.query.filter_by(product_id=id, title=detail.title).first()
            if productdesc:
              
                productdesc.title = detail.title
                productdesc.description = detail.description
            else:
               
                new_productdesc = ProductDescription(product_id=id, title=detail.title, description=detail.description)
                db.session.add(new_productdesc)
        
        
        db.session.commit()
        response = Productout.from_orm(product)
        return response.dict()


@admin.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id: int):
    if request.method == 'DELETE':
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return {'message': f'Product {product} deleted successfully'}



@admin.route("/usersignup",methods=['POST'])
@validate()
def userSignUp(body:Userin):
    if request.method=='POST':
        password=generate_password_hash(body.password)
        new_user=User(
            name=body.name,
            username=body.username,
            email=body.email,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        response=Userout.from_orm(new_user)
        return response.dict()
    

@admin.route("/adduserdetails",methods=['PUT'])
@validate()
def addUserDetails(body:Userdetails):
    if request.method=="PUT":
        id=body.id
        print(id)
        user=User.query.get_or_404(id)
            
        user.phone = body.phone
        user.county = body.county
        user.town = body.town
        user.created=datetime.now().date()
        user.dob = body.dob
        user.gender = body.gender
        user.companyname = body.companyname
        user.address = body.address
        print(datetime.now())
    
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        response = Userout.from_orm(user)
        return response.dict()
    


@admin.route("/viewusers",methods=['GET'])
@validate()
def viewUsers():
    if request.method=="GET":
        users=User.query.all()
        user_data = [Userout.from_orm(user).dict() for user in users]
    return jsonify(user_data)

@admin.route("/addorders",methods=['POST'])
@validate()
def addOrders(body:Orderin):
    if request.method=="POST":
        price_tuple = Product.query.with_entities(Product.price).filter(Product.id == body.product_id).first()

        
        if price_tuple:
            price = price_tuple[0]  
        else:
            return ("invalid product")

        #
        total_price = price * body.quantity
        new_order=Order(
        customer=body.customer,
        product_id=body.product_id,
        quantity=body.quantity,
        order_date=datetime.now().date(),
        total_price=total_price
                 )
        db.session.add(new_order)
        db.session.commit()
        response=Orderout.from_orm(new_order)
        return response.dict()
    




@admin.route("/testlogin", methods=['POST'])
def testlogin():
    if request.method == 'POST':
        try:
            body = Testlogin(**request.json)
            email = body.email
            print(body.email, body.password)
            valid_user = User.query.filter(User.email == email).first()
            if valid_user and check_password_hash(valid_user.password, body.password):
                User.generate_auth_token()
                return jsonify({"token": token})
            else:
                return jsonify({"message": "Invalid email or password"}), 401
        except ValidationError as e:
            return jsonify({"message": "Invalid request body", "errors": e.errors()}), 400
    return jsonify({"message": "Invalid method"}), 405
@admin.route("/testerroute")
@token_required
def testerroute():
    return("hey there I' m in ")




            
        



   



