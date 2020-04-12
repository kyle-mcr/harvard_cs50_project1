import os
import requests
import csv
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "BWfT8CRtFGbWIZebNdceyQ", "isbns": "9781632168146"})
print(res.json())

from flask import Flask, session, request, render_template, redirect, flash, redirect, url_for, logging
from flask_session import Session
from sqlalchemy import create_engine
from functools import wraps
from wtforms import Form, StringField, BooleanField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("home.html")

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()
    print("Got Post Info")
    print(request.form)
    form = RegisterForm(request.form)
    if request.method =='POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
       
       # Insert register into DB
        db.execute('INSERT INTO users(name, username, password) VALUES(:name, :username, :password)', {'name':name, 'username':username, 'password':password})
        print("Insert into db complete")

        # Commit changes to database
        db.commit()
        print("db commit complete")
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Get user by username
        result = db.execute("SELECT * FROM users WHERE username LIKE :username", {"username": username}).fetchone()
        print(result)
        print(result[0])
        if result[0] > 0:
            # Get stored hash
            password = result['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('search'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            db.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
@is_logged_in
def search():
    username = session['username']
    all_books = db.execute("SELECT * FROM books").fetchmany(6)[1:]
    # search function for books
    if request.method == "POST":
        searchQuery = request.form.get("searchQuery")
        # return value from the search
        searchResult = db.execute("SELECT isbn, author, title FROM books WHERE isbn iLIKE '%"+searchQuery+"%' OR author iLIKE '%"+searchQuery+"%' OR title iLIKE '%"+searchQuery+"%'").fetchall()
        # add search result to the list
        session["books"] = []
        # add the each result to the list
        for i in searchResult:
            session["books"].append(i)
        if len(session["books"])==0:
            return "No list!"
        return render_template("search.html", books = session["books"], searchQuery = searchQuery, username=username)
    return render_template("search.html", all_books=all_books, username=username )

@app.route('/books', methods=['GET', 'POST'])
@is_logged_in
def books():
    username = session['username']
    all_books = db.execute("SELECT * FROM books LIMIT 51")
    return render_template("books.html", all_books=all_books, username=username )



if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(debug=True)