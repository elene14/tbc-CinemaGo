from ext import app, db
from flask import render_template, redirect, request, url_for
from models import Movie, User, Review

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash


#LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def is_admin_user():
    return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

#HOME
@app.route("/")
def home():
    movies = Movie.query.all()
    return render_template("CinemaGo.html", movies=movies)

#MOVIES
@app.route("/movies")
def movies_page():
    movies = Movie.query.all()
    return render_template("movies.html", movies=movies)

#MOVIE DETAILS+REVIEWS
@app.route("/movie/<int:id>")
def movie(id):
    movie = db.session.get(Movie, id)
    reviews = Review.query.filter_by(movie_id=id).all()
    return render_template("movie_detail.html", movie=movie, reviews=reviews)

#REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            return "Account with this email already exists!"

        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html", form=form)

#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):

            if user.email == "elenemamaiashvili14@gmail.com" and not user.is_admin:
                user.is_admin = True
                db.session.commit()
                print(f"Auto-promoted {user.email} to Admin on login!")

            login_user(user)
            return redirect("/profile")
        else:
            print("Wrong Email or password")
    return render_template("login.html", form=form)

#PROFILE
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

#LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

#ADD MOVIE
@app.route("/add_movie", methods=["GET", "POST"])
@login_required
def add_movie():
    if not is_admin_user():
        return "Access Denied", 403

    if request.method == "POST":
        movie = Movie(name=request.form["name"],
                      genre=request.form["genre"],
                      year=request.form["year"],
                      rating=request.form["rating"],
                      duration=request.form["duration"],
                      image=request.form["image"],
                      description=request.form["description"])
        db.session.add(movie)
        db.session.commit()
        return redirect("/movies")
    return render_template("add_movie.html")


#EDIT MOVIE
@app.route("/edit_movie/<int:id>", methods=["GET", "POST"])
@login_required
def edit_movie(id):
    if not is_admin_user():
        return "Access Denied", 403

    movie = db.session.get(Movie, id)
    if request.method == "POST":
        movie.name = request.form["name"]
        movie.genre = request.form["genre"]
        movie.year = request.form["year"]
        movie.rating = request.form["rating"]
        movie.duration = request.form["duration"]
        movie.image = request.form["image"]
        movie.description = request.form["description"]
        db.session.commit()
        return redirect("/movies")
    return render_template("edit_movie.html", movie=movie)

#DELETE MOVIE
@app.route("/delete_movie/<int:id>")
@login_required
def delete_movie(id):
    if not is_admin_user():
        return "Access Denied",

    movie = db.session.get(Movie, id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect("/movies")

#ADD REVIEW
@app.route("/add_review/<int:movie_id>", methods=["POST"])
@login_required
def add_review(movie_id):
    review = Review(text=request.form["text"],
                    rating=request.form["rating"],
                    user_id=current_user.id,
                    movie_id=movie_id)
    db.session.add(review)
    db.session.commit()
    return redirect(f"/movie/{movie_id}")