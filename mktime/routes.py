import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from mktime import app, db, bcrypt
from mktime.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ProductForm
from mktime.models import User, Post, Product
from flask_login import login_user, current_user, logout_user, login_required

#if home route render home page
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

#if products route, get all products and render
@app.route("/products")
def products():
    products = Product.query.all()
    return render_template('products.html', title='Products', products=products)

#if about route, render about page
@app.route("/about")
def about():
    return render_template('about.html', title='About')

#if login route, different courses of action depending on method 
#if auth, then redirect to home
#if form.validate_on_submit can only happen on POST request
#if ok go home/next
#if fail, flash message
#and if none of the above, must be a GET request to load the form
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm() #see forms.py for definition
    if form.validate_on_submit(): #if passed validation rules in forms.py
        user = User.query.filter_by(email=form.email.data).first() #find user
        if user and bcrypt.check_password_hash(user.password, form.password.data): #check password matches db
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #if next is in url query string get args eg http://localhost:5000/login?next=%2Faccount
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful, please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#if logged in redirect home
#instantiate reg form
#if orm.validate_on_submit, must be POST, so store user to db
#else must be GET so render form
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has now been created, you are now able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#if logout route then do logout on flask_login 
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    # rename file to avoid conflicts
    random_hex = secrets.token_hex(8) #make a random hex string
    _, f_ext = os.path.splitext(form_picture.filename) # get the file extension and chuck original filename (._)
    picture_fn = random_hex + f_ext #make new random file name and ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',  picture_fn) #get the correct location
    # resize image 
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save file with new name and size
    i.save(picture_path)
    return picture_fn

def save_product_picture(form_picture):
    # rename file to avoid conflicts
    random_hex = secrets.token_hex(8) #make a random hex string
    _, f_ext = os.path.splitext(form_picture.filename) # get the file extension and chuck original filename (._)
    picture_fn = random_hex + f_ext #make new random file name and ext
    picture_path = os.path.join(app.root_path, 'static/product_pics',  picture_fn) #get the correct location
    # resize image 
    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save file with new name and size
    i.save(picture_path)
    return picture_fn

#view/change account details
#GET = render form with logged in user used in form
#POST and validated = save picture and save user to db
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('You account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

#CRUD operations for Post model
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title="Contact Us", form=form, legend="Contact Us")
    
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method =='GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title="Update Post", image_file=image_file, form=form, legend="Update Post")

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))

#end of Post CRUD operations

# add new products, not protected route but should be under normal use
#if get request create form and render
#if post request, validate form, save picture as thumb and write product to db
@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required 
def new_product():
    form = ProductForm() 
    if form.validate_on_submit():
        image_file = url_for('static', filename='product_pics/watch_default.jpg') #set default pic
        if form.picture.data: #and if something different added change it
            image_file = save_product_picture(form.picture.data)
        product = Product(name=form.name.data, description=form.description.data, 
                          price=form.price.data, gender=form.gender.data, image_file=image_file,
                          in_stock=form.in_stock.data)
        db.session.add(product)
        db.session.commit()
        flash('The Product has been created!', 'success')
        return redirect(url_for('new_product'))
    return render_template('create_product.html', title="New Product", form=form, legend="New Product")

#would normally be protected route to read posts
#get all posts and render template
@app.route("/admin/posts")
@login_required
def admin_posts():
    posts = Post.query.all()
    return render_template('admin_posts.html', posts=posts)