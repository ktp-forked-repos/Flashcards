from flask import Flask, render_template, redirect, request, g, session, url_for, flash
from model import User, Post, Collection
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    if current_user.is_authenticated():
        collections = Collection.query.filter_by(user_id=current_user.id)
        return render_template("index.html", collections=collections)
    else:
        return render_template("landing.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/post/<int:id>")
def view_post(id):
    post = Post.query.get(id)
    return render_template("post.html", post=post)

@app.route("/post/new")
@login_required
def new_post():
    return render_template("new_post.html")

@app.route("/post/new", methods=["POST"])
@login_required
def create_post():
    form = forms.NewPostForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_post.html")

    post = Post(title=form.title.data, body=form.body.data)
    current_user.posts.append(post) 
    
    model.session.commit()
    model.session.refresh(post)

    return redirect(url_for("view_post", id=post.id))

@app.route("/collection/<int:id>")
def view_collection(id):
    collection = Post.query.get(id)
    return render_template("collection.html", collection=collection)

@app.route("/collection/new")
@login_required
def new_collection():
    return render_template("new_collection.html")

@app.route("/collection/new", methods=["POST"])
@login_required
def create_collection():
    form = forms.NewCollectionForm(request.form)
    if not form.validate():
        flash("Error, all fields are required")
        return render_template("new_collection.html")

    collection = Collection(title=form.title.data, description=form.description.data, user_id=current_user.id)
    current_user.collections.append(collection) 
    
    model.session.add(collection)
    model.session.commit()
    model.session.refresh(collection)

    return redirect(url_for("index"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def authenticate():
    form = forms.LoginForm(request.form)
    if not form.validate():
        flash("Incorrect username or password") 
        return render_template("login.html")

    email = form.email.data
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.authenticate(password):
        flash("Incorrect username or password") 
        return render_template("login.html")

    login_user(user)
    return redirect(request.args.get("next", url_for("index")))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def create_user():
    form = forms.RegisterForm(request.form)
    print "form variable!"
    if not form.validate():
        flash("username not valid")
        return render_template("register.html")

    first_name=form.first_name.data
    last_name=form.last_name.data
    email=form.email.data
    password=form.password.data

    existing = User.query.filter_by(email=email).first()
    if existing:
        flash("username already taken")
    else:
        user = User(email=email, first_name=first_name, last_name=last_name, password=password, salt="random")
        user.set_password(password)

        model.session.add(user)
        model.session.commit()
        login_user(user)

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
