from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User
from openai import OpenAI
import os

app = Flask(__name__)

# ================= SECRET KEY =================

app.secret_key = "juned_chatbot_secret"


# ================= DATABASE =================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ================= OPENROUTER =================

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

client = None

if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )


# ================= HOME =================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return "Please fill all fields!"

        user = User.query.filter_by(email=email).first()

        if user:
            return "Email already exists!"

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("register.html")


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user is None:
        return "User Not Found!"

    if not check_password_hash(user.password, password):
        return "Wrong Password!"

    session["user_id"] = user.id
    session["user_name"] = user.name

    return redirect(url_for("dashboard"))


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# ================= CHATBOT PAGE =================

@app.route("/chatbot")
def chatbot():

    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "chatbot.html",
        name=session["user_name"]
    )


# ================= OPENROUTER AI CHAT =================

@app.route("/ask", methods=["POST"])
def ask():

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first."
        }), 401

    if client is None:
        return jsonify({
            "error": "OpenRouter API key is not configured."
        }), 500

    data = request.get_json(silent=True) or {}

    question = data.get("message", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a message."
        }), 400

    try:

        response = client.chat.completions.create(

            model="openrouter/free",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Answer the user's questions clearly, "
                        "accurately and in simple language."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response.choices[0].message.content

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("OPENROUTER ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)