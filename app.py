from flask import Flask, render_template, redirect, request, g, url_for, session
import sqlite3
import os
from os import urandom
import json
from questions import questions

app = Flask(__name__)
app.secret_key= urandom(24)

DATABASE = 'findnorth.db'
app.config['DATABASE'] = DATABASE

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            not request.form.get("email")
            or not request.form.get("password")
        ): 
            return render_template("error.html", message="Enter both email and password to login")
        email = request.form.get("email")
        passw = request.form.get("password")
        # print(f"Email: {email}, Password: {passw}")  # Debug log

        db = get_db()   
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
            return render_template("error.html", message="Email not present in database")
        # print(f"Stored password: {user['passw']}")  # Debug log
        if user["passw"] == passw:  
            # Store user information in the session
            session["user_id"] = user["id"]
            session["name"] = user["first_name"]
            return redirect(url_for("profile"))
        else:
            return render_template("error.html", message="Incorrect password")
    return render_template("login.html")

@app.route("/questionnaire", methods = ["GET", "POST"])
def questionnaire():
    if request.method == "POST":
        ques = [f"question{i}" for i in range(1, 21)]
        missing_answers = [q for q in ques if not request.form.get(q)]
        if missing_answers:
            return render_template("error.html", message="Please answer all questions.")
        
        total = 0
        for q in ques:
            ans = request.form.get(q)
            if ans is not None:
                total += int(ans)

        user_id = session.get('user_id')  # Replace with the appropriate way to get user ID
        sql = """
            INSERT INTO quest_responses (user_id, responses, score, pcl5result) 
            VALUES (?, ?, ?, ?)
        """
        db = get_db()
        db.execute(sql, (user_id, total))
        db.commit()
        return redirect(url_for("profile"))
    
    return render_template("questionnaire.html", questions=questions)

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Ensure all required fields are provided
        if (
            not request.form.get("first")
            or not request.form.get("last")
            or not request.form.get("email")
            or not request.form.get("password")
            or not request.form.get("sex")
            or not request.form.get("age")
            or not request.form.get("role")
        ):
            return render_template("error.html", message= "All fields are required to create an account.")

        email = request.form.get("email")
        passw = request.form.get("password")
        first_name = request.form.get("first").capitalize()  # Capitalizing first name
        last_name = request.form.get("last").capitalize()    # Capitalizing last name
        age = request.form.get("age")
        sex = request.form.get("sex")
        user_role = request.form.get("role")  # This can be either 'doc' or 'patient'

        # Ensure that user_role is valid
        if user_role not in ['doc', 'patient']:
            return render_template("error.html", message="Invalid role selected.")

        db = get_db()  # Assuming you have a helper function to get the DB connection
        cursor = db.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("error.html", message="Email already exists.")

        # Insert the new user into the users table
        cursor.execute(
            "INSERT INTO users (email, first_name, last_name, passw, user_role, age, sex) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (email, first_name, last_name, passw, user_role, age, sex),
        )
        db.commit()

        # Store user information in the session after inserting
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        session["user_id"] = user["id"]  # Store the user ID in the session

        return redirect(url_for("profile"))  # Redirect to the user's profile or dashboard

    return render_template("signup.html")


init_db()

if __name__ == "__main__":
    app.run(debug=True)