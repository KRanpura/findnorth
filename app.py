from flask import Flask, render_template, redirect, request, g, url_for, session,jsonify
import sqlite3
import os
from os import urandom
import json
from questions import questions
import pandas as pd
from model.ptsd_model import PTSDModel

app = Flask(__name__)
ptsd_model = PTSDModel()

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
            session["role"] = user["user_role"]
            return redirect(url_for("profile"))
        else:
            return render_template("error.html", message="Incorrect password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/forum")
def forum():
    db = get_db()
    cursor = db.cursor()
    # Fetch posts along with the user's role
    cursor.execute("""
        SELECT forum_posts.*, users.user_role
        FROM forum_posts
        JOIN users ON forum_posts.user_id = users.id
    """)
    posts = cursor.fetchall()

    # Convert sqlite3.Row objects to dictionaries
    posts = [dict(post) for post in posts]
    # Fetch replies and include the user role
    for post in posts:
        cursor.execute("""
            SELECT forum_replies.*, users.user_role
            FROM forum_replies
            JOIN users ON forum_replies.user_id = users.id
            WHERE forum_replies.og_post_id = ?
        """, (post['id'],))
        replies = cursor.fetchall()

        # Convert replies to dictionaries
        post['replies'] = [dict(reply) for reply in replies]
    return render_template("forum.html", posts=posts)

@app.route("/reply_post/<int:post_id>", methods=["GET", "POST"])
def reply_post(post_id):
    db = get_db()
    cursor = db.cursor()
    
    # Fetch the post data to display
    cursor.execute("SELECT * FROM forum_posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    
    if request.method == "POST":
        reply_content = request.form.get("reply_content")
        user_id = session["user_id"]
        
        # Insert the reply into the database
        cursor.execute(
            "INSERT INTO forum_replies (user_id, og_post_id, content) VALUES (?, ?, ?)",
            (user_id, post_id, reply_content),
        )
        db.commit()
        return redirect(url_for("forum"))

    # Send post details to the template
    return render_template("reply_post.html", post=post)

@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    if request.method == "POST":
        ques = [f"q{i}" for i in range(1, 21)]
        missing_answers = [q for q in ques if not request.form.get(q)]
        if missing_answers:
            return render_template("error.html", message="Please answer all questions.")
        
        total = 0
        for q in ques:
            ans = request.form.get(q)
            if ans is not None:
                total += int(ans)

        severity_level = severity(total)

        user_id = session.get('user_id')  # Replace with the appropriate way to get user ID
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT age, sex FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        age = user_data['Age']
        sex = user_data['Sex']

        sql = """
            INSERT INTO quest_responses (user_id, pcl5result) 
            VALUES (?, ?)
        """
        db.execute(sql, (user_id, total))
        db.commit()

        # Prepare data for the prediction model
        input_data = pd.DataFrame({
            'Age': [int(age)],
            'Sex': [0 if sex == 'F' else 1], 
            'PCL-Score': [int(total)]  # Ensure the column name is exactly as in the trained model
        })

        # Get the prediction result
        prediction = ptsd_model.predict(input_data)

        return render_template("result.html", 
                               age=age, 
                               sex=sex, 
                               pcl_score=total,
                               severity=severity_level, 
                               ptsd_probability=prediction[0])
    return render_template("questionnaire.html", questions=questions)

def severity(pcl_score):
    """
    Categorizes PCL-5 scores into string values
    """
    if 0 <= pcl_score <= 31:
        return "None/Resilience"
    if 32 <= pcl_score <= 47:
        return "Mild"
    if 48 <= pcl_score <=63:
        return "Moderate"
    if 64 <= pcl_score <=80:
        return "Serious"
    else:
        return "Invalid"


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/make_post")
def makepost():
    return render_template("new_post.html")

@app.route("/add_post", methods=["GET", "POST"])
def addpost():
    if request.method == "POST":
        if (
            not request.form.get("title")
            or not request.form.get("content")
        ):
            return render_template("error.html")
        title = request.form.get("title")
        content = request.form.get("content")
        userid = session["user_id"]
        db =get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO forum_posts (user_id, title, content) VALUES (?, ?, ?)",
            (userid, title, content),
        )
        db.commit()
        return render_template("thank_you.html")

    return render_template("new_post.html")

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
        session["name"] = user["first_name"]
        session["role"] = user["user_role"]
        return redirect(url_for("profile"))  # Redirect to the user's profile or dashboard

    return render_template("signup.html")





init_db()

if __name__ == "__main__":
    app.run(debug=True)

    