from flask import (
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    jsonify,
    make_response,
    send_from_directory,
)

from shop import db
from flask_pydantic import validate

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from shop.models import User, Product, ProductDescription, Order,ProductImages
from shop.decorators import token_required
from .forms import RegistrationForm, LoginForm
from shop.mail import send_email, tokenizationsession, tokenizationconfirmation
from flask_httpauth import HTTPTokenAuth
from ..schemas import (
    Productin,
    Productout,
    ProductDescriptionin,
    Productdescriptionout,
    Userin,
    Userout,
    Userdetails,
    Orderin,
    Orderout,
    Testlogin,
)
from typing import List

import jwt
import datetime
from datetime import datetime, timedelta
from pydantic import ValidationError

import os
from PIL import Image
import uuid
from . import admin
from .authentication import basic_auth

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    # Your token verification logic here
    return True  # Replace with your actual verification logic


#


@admin.route("/admin")
@auth.login_required
@token_required
def indexpage():

    if "name" not in session:
        flash(f"please login first", "danger")
        return redirect(url_for("admin.login"))
    print(session)
    # products=Addproduct.query.all()
    return render_template("admin/index.html", title="Admin Page")


@admin.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        vuser = User.query.filter_by(email=form.email.data).first()
        if not vuser:
            hash_password = generate_password_hash(form.password.data)
            user = User(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                password=hash_password,
            )

            db.session.add(user)
            name = form.name.data
            flash(f"Welcome {form.name.data}.Thanks for registering.Success")
            db.session.commit()
            token = user.generate_confirmation_token()
            send_email(
                user.email,
                "Confirm Your Account",
                "mail/register",
                user=user,
                token=token,
            )
            send_email(
                current_app.config["FLASKY_ADMIN"],
                " New User",
                "mail/new_user",
                user=user,
            )

            return redirect(url_for("admin.indexpage"))

        else:
            flash("User already exists")
            return redirect(url_for("admin.login"))
    return render_template("admin/register.html", form=form, title="Registration Page")


@admin.route("/", methods=["GET", "POST"])
@auth.login_required
@token_required
def something():
    return redirect(url_for("admin.indexpage"))
    return render_template("admin/index.html")


@admin.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, form.remember_me.data)
            name = user.name

            session["name"] = name
            flash(f"Welcome Back {name}.Successful Login")
            email = form.email.data

            token = tokenizationsession(name)

            print(f"?token={token}")

            return redirect(
                request.args.get("next")
                or url_for("admin.indexpage", token=token, _external=True)
            )
        else:
            flash(f" Wrong Password", "danger")

            return redirect(url_for("admin.login"))
    return render_template(
        "admin/login.html", title="Login Page", form=form, email=session.get("email")
    )


@admin.route("/confirm/<token>")
def confirm(token):
    print(current_user.confirm(token))

    if current_user.confirmed:
        return redirect(url_for("admin.indexpage", token=token, _external=True))
    elif current_user.confirm(token):

        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("admin.indexpage"))


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin.login"))  #


@admin.route("/addproducts", methods=["POST"])
@validate()
def addproduct(body: Productin):
    if request.method == "POST":
        new_product = Product(
            category=body.category,
            name=body.name,
            description=body.description,
            price=body.price,
        )
        db.session.add(new_product)
        db.session.commit()
        id = new_product.id
        for detail in body.detail:
            new_productdesc = ProductDescription(
                product_id=id, title=detail.title, description=detail.description
            )
            db.session.add(new_productdesc)
        db.session.commit()
        response = Productout.from_orm(new_product)
        return response.dict()


@admin.route("/products/<int:id>")
def view_product(id: int):
    if request.method == "GET":
        product = Product.query.get_or_404(id)

        response = Productout.from_orm(product)
        return response.dict()


@admin.route("/products")
@login_required
def view_product_all():
    if request.method == "GET":
        product = Product.query.all()

        response_list = []
        for prod in product:
            response_list.append(Productout.from_orm(prod).dict())

        return response_list


@admin.route("/products/detail", methods=["POST", "GET"])
@validate()
def addproductdetail(body: ProductDescriptionin):
    new = ProductDescription(**body.dict())
    db.session.add(new)
    db.session.commit()
    response = Productdescriptionout.from_orm(new)
    return response.dict()


@admin.route("/products/<int:id>", methods=["PUT"])
@validate()
def edit_product(id: int, body: Productin):
    if request.method == "PUT":
        product = Product.query.get_or_404(id)
        product.name = body.name
        product.category = body.category
        product.description = body.description
        product.price = body.price
        for detail in body.detail:
            productdesc = ProductDescription.query.filter_by(
                product_id=id, title=detail.title
            ).first()
            if productdesc:

                productdesc.title = detail.title
                productdesc.description = detail.description
            else:

                new_productdesc = ProductDescription(
                    product_id=id, title=detail.title, description=detail.description
                )
                db.session.add(new_productdesc)

        db.session.commit()
        response = Productout.from_orm(product)
        return response.dict()


@admin.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id: int):
    if request.method == "DELETE":
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return {"message": f"Product {product} deleted successfully"}


@admin.route("/usersignup", methods=["POST"])
@validate()
def userSignUp(body: Userin):
    if request.method == "POST":
        password = generate_password_hash(body.password)
        new_user = User(
            name=body.name, username=body.username, email=body.email, password=password
        )
        db.session.add(new_user)
        db.session.commit()
        response = Userout.from_orm(new_user)
        return response.dict()


@admin.route("/adduserdetails", methods=["PUT"])
@validate()
def addUserDetails(body: Userdetails):
    if request.method == "PUT":
        id = body.id
        print(id)
        user = User.query.get_or_404(id)

        user.phone = body.phone
        user.county = body.county
        user.town = body.town
        user.created = datetime.now().date()
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


@admin.route("/viewusers", methods=["GET"])
@validate()
def viewUsers():
    if request.method == "GET":
        users = User.query.all()
        user_data = [Userout.from_orm(user).dict() for user in users]
    return jsonify(user_data)


@admin.route("/addorders", methods=["POST"])
@validate()
def addOrders(body: Orderin):
    if request.method == "POST":
        price_tuple = (
            Product.query.with_entities(Product.price)
            .filter(Product.id == body.product_id)
            .first()
        )

        if price_tuple:
            price = price_tuple[0]
        else:
            return "invalid product"

        #
        total_price = price * body.quantity
        new_order = Order(
            customer=body.customer,
            product_id=body.product_id,
            quantity=body.quantity,
            order_date=datetime.now().date(),
            total_price=total_price,
        )
        db.session.add(new_order)
        db.session.commit()
        response = Orderout.from_orm(new_order)
        return response.dict()


@admin.route("/testlogin", methods=["POST"])
@basic_auth.login_required
def testlogin():
    if request.method == "POST":
        try:
            body = Testlogin(**request.json)
            email = body.email
            print(body.email, body.password)
            valid_user = User.query.filter(User.email == email).first()
            if valid_user and check_password_hash(valid_user.password, body.password):
                token = valid_user.generate_auth_token()
                return jsonify({"token": token})
            else:
                return jsonify({"message": "Invalid email or password"}), 401
        except ValidationError as e:
            return (
                jsonify({"message": "Invalid request body", "errors": e.errors()}),
                400,
            )
    return jsonify({"message": "Invalid method"}), 405


@admin.route("/testerroute")
@auth.login_required
def testerroute():
    return "hey there I' m in "


from ..models import Product


@admin.route("/home", methods=["GET"])
@auth.login_required
def home():
    products = Product.query.all()
    products_list = []
    for prod in products:
        products_list.append(Productout.from_orm(prod).dict())
    # category = db.session.query(
    #     Product.category.label("category"),
    # ).distinct()
    # print(product_list, category)
    categories = db.session.query(
        Product.category.label("category"),
    ).distinct()
    categorical_products = []
    for category in categories:
        category_product = Product.query.filter(
            Product.category == category.category
        ).all()
        # print("category :", category.category)
        category_product_list = []
        for prod in category_product:
            category_product_list.append(Productout.from_orm(prod).dict())

        print("category list", category_product_list)
        for product_category in category_product_list:
            print(product_category["description"])
        print(category)
        categorical_products.append({f"{category.category}": category_product_list})
    print(categorical_products[0])
    # print(categories[1].category)
    # for product in categorical_products[0]["Phone"]:
    #     print(product["name"])

    recent = Product.query.order_by(Product.creation_date).all()
    recent_product_list = []
    for prod in recent:
        recent_product_list.append(Productout.from_orm(prod).dict())
    print(recent_product_list)

    return render_template(
        "home.html",
        products=products_list,
        categories=categories,
        category_products=categorical_products,
        recent_products=recent,
    )


@admin.route("/viewproduct", methods=["GET"])
def viewproduct():
    product = Product.query.filter(Product.id == 5).all()
    product_list = []
    for prod in product:
        product_list.append(Productout.from_orm(prod).dict())
    print(product_list[0]["detail"])

    return render_template("view_product.html", product=product_list)


# @admin.route("/uploads/<filename>")
# def get_file(filename):
#     return send_from_directory(current_app.config["UPLOADED_PHOTOS_DEST"], filename)


# @admin.route("/uploadimage", methods=["GET", "POST"])
# def uploadimage():
#     form = UploadForm()
#     if form.validate_on_submit():
#         filename = photos.save(form.photo.data)
#         file_url = url_for("get_file", filename=filename)
#     else:
#         file_url = "0761fbda692b4e1fa794cebfe833561c.jpeg"
#     return render_template("image.html", file_url=file_url, form=form)


def allowed_images(filename):
    ALLOWED_IMAGES = ["png", "jpg", "jpeg"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGES

@admin.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name[]')
        product_description = request.form.get('product_description[]')
        product_category = request.form.get('product_category')
        product_price = request.form.get('product_price')
        product_summary = request.form.get('product_summary')
        product_detail_titles = []
        product_detail_descriptions = []
        product_files = []
        image_count = int(request.form.get('image_counter'))  # Retrieve the count value
        detail_count = int(request.form.get('detail_counter'))
        title=request.form.get('product_detail_title_[5]')
        file=request.form.get('product_file_1')
        print("title:",title,"file:",file)


        new_product = Product(
            category=product_category,
            name=product_name,
            description=product_description,
            price=product_price,
            summary=product_summary
        )
        db.session.add(new_product)
        db.session.commit()
        id = new_product.id

        for i in range(1, image_count+1):
            # file = request.form.get(f'product_file_{i}')  # Access files using request.files
            photo=request.files[f'product_file_{i}']
            # Assuming `allowed_images` is a function that checks if the image is allowed
            if photo and allowed_images(photo.filename):
                filename = secure_filename(photo.filename)
                # Split the filename to get the base name and extension
                basename, extension = os.path.splitext(filename)
                # Generate a unique identifier for the filename
                unique_filename = str(uuid.uuid4()) + '_' + basename + extension
                
                # Save the original image with the unique filename
                photo.save(os.path.join(current_app.config['IMAGE_UPLOAD'], unique_filename))

                # Compress the image
                compressed_filename = basename + '_compressed' + extension
                compressed_path = os.path.join(current_app.config['IMAGE_UPLOAD'], unique_filename)
                with Image.open(os.path.join(current_app.config['IMAGE_UPLOAD'], unique_filename)) as img:
                    # Compress the image using PIL
                    img.save(compressed_path, optimize=True, quality=70)

                # Get the compressed filename with the original extension
                file = compressed_filename
                product_files.append(file)
                new_image = ProductImages(
                    product_id=id,
                    image=file

                )
                db.session.add(new_image)

        
        print("product name", product_name, "product description", product_description, "product category", product_category, "product price", product_price, "product summary", product_summary, "product detail titles", product_detail_titles, "product detail descriptions", product_detail_descriptions, "product files", product_files)
        for i in range(1, detail_count+1):
            title = request.form.get(f'product_detail_title[{i}]')
            description = request.form.get(f'product_detail_description[{i}]')
            product_detail_titles.append(title)
            product_detail_descriptions.append(description)
            new_productdesc = ProductDescription(
                product_id=id,
                title=title,
                description=description
            )
            db.session.add(new_productdesc)
        db.session.commit()

        print("product detail titles", product_detail_titles, "product detail descriptions", product_detail_descriptions)

        # Process product data and files as needed

        return 'Form submitted successfully'

    return render_template('add_product.html')
