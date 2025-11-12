from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# -------------------- DATABASE CONFIG --------------------
if os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookings.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking", backref="user", lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    service_type = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    location = db.Column(db.String(100))
    package = db.Column(db.String(50))
    addons = db.Column(db.String(200))
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# -------------------- ROUTES --------------------
@app.route("/")
def home():
    user = None
    bookings = []
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.id.desc()).all()
    return render_template("index.html", user=user, bookings=bookings)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(phone=phone).first():
            return render_template("signup.html", error="Phone number already registered")

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(name=name, phone=phone, email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash("✅ Account created! Please log in.")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]

        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            flash("✅ Login successful!")
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# -------------------- BOOKING ROUTE --------------------
@app.route("/book", methods=["GET", "POST"])
def book_service():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        booking = Booking(
            user_id=user.id,
            service_type=request.form["service_type"],
            date=request.form["date"],
            time=request.form["time"],
            location=request.form["location"],
            package=request.form["package"],
            addons=", ".join(request.form.getlist("addons")),
            payment_method=request.form["payment_method"],
            payment_status=request.form["payment_status"],
            status="Pending"
        )
        db.session.add(booking)
        db.session.commit()

        flash("✅ Booking added successfully!")
        return redirect(url_for("home"))

    return render_template("book_service.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
