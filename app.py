from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------- DATABASE CONFIG --------------------
# Use PostgreSQL on Render (via DATABASE_URL env variable)
# Fallback to local SQLite if not on Render
if os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "bookings.db")

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
    bookings = db.relationship("CarWashBooking", backref="user", lazy=True)

# Separate table just for Car Wash Bookings
class CarWashBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    car_make = db.Column(db.String(100))
    car_type = db.Column(db.String(50))
    vehicle_number = db.Column(db.String(50))
    color = db.Column(db.String(50))
    service_type = db.Column(db.String(100))
    package = db.Column(db.String(50))
    addons = db.Column(db.String(200))
    special_instructions = db.Column(db.String(300))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    location = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(20))
    promo_code = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- CREATE TABLES --------------------
with app.app_context():
    db.create_all()

# -------------------- DATA --------------------
SERVICES = [
    {"name": "Car Wash", "price": 10, "image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70"},
    {"name": "Full Detailing", "price": 60, "image": "https://images.unsplash.com/photo-1601924582971-df8fef8b2716"},
    {"name": "Haircut", "price": 15, "image": "https://images.unsplash.com/photo-1598515214280-6b0b64d6f68e"},
    {"name": "Shave", "price": 8, "image": "https://images.unsplash.com/photo-1588776814546-6044b9c1e3a3"},
]

ADS = [
    {"title": "Get 20% off your first Car Wash!", "image": "https://images.unsplash.com/photo-1605719124118-40e4a6f2e4f2"},
    {"title": "Weekend Offer: Haircut + Shave Combo", "image": "https://images.unsplash.com/photo-1621954520131-ecdf5d6f0ef9"},
]

# -------------------- ROUTES --------------------
@app.route("/")
def home():
    user = User.query.get(session["user_id"]) if "user_id" in session else None
    return render_template("index.html", user=user, services=SERVICES, ads=ADS)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(phone=phone).first():
            return render_template("signup.html", error="Phone number already registered")

        user = User(name=name, phone=phone, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")
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
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# -------------------- CAR WASH BOOKING --------------------
@app.route("/book/car-wash", methods=["GET", "POST"])
def book_carwash():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        booking = CarWashBooking(
            user_id=user.id,
            car_make=request.form["car_make"],
            car_type=request.form["car_type"],
            vehicle_number=request.form["vehicle_number"],
            color=request.form.get("color"),
            service_type=request.form["service_type"],
            package=request.form["package"],
            addons=", ".join(request.form.getlist("addons")),
            special_instructions=request.form.get("special_instructions"),
            date=request.form["date"],
            time=request.form["time"],
            location=request.form["location"],
            payment_method=request.form["payment_method"],
            payment_status=request.form["payment_status"],
            promo_code=request.form.get("promo_code")
        )
        db.session.add(booking)
        db.session.commit()
        flash("✅ Car Wash Booking Submitted Successfully!")
        return redirect(url_for("home"))

    return render_template("book_carwash.html", user=user)

if __name__ == "__main__":
    # When running locally, use Flask dev server
    app.run(debug=True, host="0.0.0.0")
