from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tour.db"
app.secret_key = "secret"
db = SQLAlchemy(app)
app.app_context().push()
# db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "You need to login to access this page"

# @app.before_first_request
# def create_tables():
#     db.create_all()
#     # logout previous users
#     logout_user()


@app.route("/")
def home():
    if current_user.is_authenticated and current_user.role == "admin":
        return render_template(
            "index.html", login=True, user=current_user.username, isAdmin=True
        )
    elif current_user.is_authenticated and current_user.role == "customer":
        return render_template(
            "index.html", login=True, user=current_user.username, isCustomer=True
        )
    else:
        return render_template("index.html")


@app.route("/about")
def about_us():
    return render_template("about_us.html")


@app.route("/contact")
def contact_us():
    return render_template("contact.html")


# Create tables in the database


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    # print(request.data)
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        mobile = data.get("mobile")
        email = data.get("email")
        address = data.get("address")
        role = data.get("role")
        user = User(username, password, mobile, email, address, role)
        db.session.add(user)
        db.session.commit()
        return render_template("login.html", message="User Created")
    else:
        return render_template("register.html", message="Invalid Request")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return render_template("index.html", login=True, user=user.username)
            else:
                return render_template("login.html", message="Invalid Password")
        else:
            return render_template("login.html", message="User not found")
    else:
        return jsonify({"message": "User not found"})


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html", message="Logged out", login=False)
    return jsonify({"message": "Logged out"})


@app.route("/profile")
@login_required
def profile():
    return jsonify(
        {
            "username": current_user.username,
            "mobile": current_user.mobile,
            "email": current_user.email,
            "address": current_user.address,
            "role": current_user.role,
        }
    )


"""Travel Destinations Section"""


@app.route("/destinations")
def destinations():
    destinations = Destination.query.all()
    userRole = current_user.role if current_user.is_authenticated else None
    isAdmin = True if userRole == "admin" else False
    isCustomer = True if userRole == "customer" else False
    return render_template(
        "destinations.html",
        destinations=destinations,
        isAdmin=isAdmin,
        isCustomer=isCustomer,
        user=current_user.username if current_user.is_authenticated else None,
    )


@app.route("/view_destination/<int:destination_id>", methods=["GET", "POST"])
def view_destination(destination_id):
    destination = Destination.query.get(destination_id)
    return render_template("view_destination.html", destination=destination)


@app.route("/addDestination", methods=["GET"])
@login_required
def add_destination_page():
    if current_user.role == "admin":
        return render_template("add_destinations.html")


@app.route("/addDestination", methods=["POST"])
@login_required
def add_destination():
    data = request.form
    name = data.get("name")
    description = data.get("description")
    image_url = data.get("image_url")
    date = data.get("date")
    price = data.get("price")
    available_seats = data.get("available_seats")

    # Explicitly specify parameter names when creating Destination object
    destination = Destination(
        name=name,
        description=description,
        image_url=image_url,
        date=date,
        price=price,
        available_seats=available_seats,
    )

    db.session.add(destination)
    db.session.commit()
    print("Destination Added")

    return render_template("index.html", message="Destination Added")


"""Tour Packages Section"""


@app.route("/packages")
def packages():
    packages = Package.query.all()
    userRole = current_user.role if current_user.is_authenticated else None
    isAdmin = True if userRole == "admin" else False
    isCustomer = True if userRole == "customer" else False
    return render_template(
        "tours.html",
        packages=packages,
        isAdmin=isAdmin,
        isCustomer=isCustomer,
        user=current_user.username if current_user.is_authenticated else None,
    )


@app.route("/addPackage", methods=["GET"])
@login_required
def add_package_page():
    if current_user.role == "admin":
        return render_template("add_package.html")


@app.route("/addPackage", methods=["POST"])
@login_required
def add_package():
    data = request.form
    name = data.get("name")
    locations = data.get("locations")
    description = data.get("description")
    image_url = data.get("image_url")
    date = data.get("date")
    price = data.get("price")
    available_seats = data.get("available_seats")

    # Explicitly specify parameter names when creating Package object
    package = Package(
        name=name,
        # locations=locations,
        description=description,
        image_url=image_url,
        date=date,
        price=price,
        available_seats=available_seats,
    )

    db.session.add(package)
    db.session.commit()
    print("Package Added")
    return render_template("index.html", message="Package Added")


@app.route("/view_package/<int:package_id>", methods=["GET", "POST"])
def view_package(package_id):
    package = Package.query.get(package_id)
    return render_template("view_package.html", package=package)


@app.route("/delete_package/<int:package_id>", methods=["GET", "POST"])
@login_required
def delete_package(package_id):
    # package = Package.query.get(package_id)
    # if package:
    #     db.session.delete(package)
    #     db.session.commit()
    #     flash("Package deleted successfully", "success")
    # else:
    #     flash("Package not found", "error")
    # return redirect(url_for("packages"))
    return redirect(
        url_for("packages", msg=True, message="Package deleted successfully")
    )


@app.route("/delete_destination/<int:destination_id>", methods=["GET", "POST"])
@login_required
def delete_destination(destination_id):
    # destination = destination.query.get(destination_id)
    # if destination:
    #     db.session.delete(destination)
    #     db.session.commit()
    #     flash("destination deleted successfully", "success")
    # else:
    #     flash("destination not found", "error")
    # return redirect(url_for("destinations"))
    return redirect(
        url_for("destinations", msg=True, message="destination deleted successfully")
    )


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    mobile = db.Column(db.String(10))
    email = db.Column(db.String(100))
    address = db.Column(db.String(100))
    role = db.Column(db.String(100))

    def __init__(self, username, password, mobile, email, address, role):
        self.username = username
        self.password = password
        self.mobile = mobile
        self.email = email
        self.address = address
        self.role = role

    def __repr__(self):
        return f"<User {self.username}>"


class Destination(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available_seats = db.Column(db.Integer, default=0)

    def __init__(self, name, description, image_url, date, price, available_seats):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.date = date
        self.price = price
        self.available_seats = available_seats

    def __repr__(self):
        return f"<Destination {self.name}>"


class Package(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available_seats = db.Column(db.Integer, default=0)

    def __init__(self, name, description, image_url, date, price, available_seats):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.date = date
        self.price = price
        self.available_seats = available_seats

    def __repr__(self):
        return f"<Package {self.name}>"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=True)
    destination_id = db.Column(
        db.Integer, db.ForeignKey("destinations.id"), nullable=True
    )
    seats = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.String(100), nullable=True)
    user = db.relationship("User", backref="bookings")
    package = db.relationship("Package", backref="bookings")
    destination = db.relationship("Destination", backref="bookings")

    def __init__(
        self, user_id, package_id, destination_id, seats, total_price, booking_date
    ):
        self.user_id = user_id
        self.package_id = package_id
        self.destination_id = destination_id
        self.seats = seats
        self.total_price = total_price
        self.booking_date = booking_date

    def __repr__(self):
        return f"<Booking {self.id}>"


@app.route("/book_package/<int:package_id>", methods=["GET"])
@login_required
def book_package_page(package_id):
    package = Package.query.get(package_id)
    if package:
        return render_template("book_package.html", package=package, message=None)
    else:
        return render_template("index.html", message="Package not found")


@app.route("/book_package/<int:package_id>", methods=["POST"])
@login_required
def book_package(package_id):
    package = Package.query.get(package_id)
    if package:
        data = request.form
        seats = data.get("seats")
        total_price = int(seats) * package.price
        booking_date = package.date
        booking = Booking(
            current_user.id, package_id, 0, seats, total_price, booking_date
        )
        # update available seats
        package.available_seats -= int(seats)
        db.session.add(booking)
        db.session.commit()
        return render_template("index.html", message="Booking Successful")
    else:
        return render_template("index.html", message="Package not found")


@app.route("/book_destination/<int:destination_id>", methods=["GET"])
@login_required
def book_destination_page(destination_id):
    destination = Destination.query.get(destination_id)
    if destination:
        return render_template("book_destination.html", destination=destination)
    else:
        return render_template("index.html", message="Destination not found")


@app.route("/book_destination/<int:destination_id>", methods=["POST"])
@login_required
def book_destination(destination_id):
    destination = Destination.query.get(destination_id)
    if destination:
        data = request.form
        seats = data.get("seats")
        total_price = int(seats) * destination.price
        booking_date = destination.date
        booking = Booking(
            current_user.id, 0, destination_id, seats, total_price, booking_date
        )
        # update available seats
        destination.available_seats -= int(seats)
        db.session.add(booking)
        db.session.commit()
        return render_template("index.html", message="Booking Successful")
    else:
        return render_template("index.html", message="Destination not found")


@app.route("/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return render_template(
            "index.html", message="You are not authorized to access this page"
        )
    bookings = Booking.query.all()  # Get all bookings
    booked_destinations = [
        (
            booking,
            User.query.get(booking.user_id),
            Destination.query.get(booking.destination_id),
        )
        for booking in bookings
        if booking.destination_id
    ]  # Fetch user, destination, and package details for booked destinations
    booked_tour_packages = [
        (
            booking,
            User.query.get(booking.user_id),
            Package.query.get(booking.package_id),
        )
        for booking in bookings
        if booking.package_id
    ]
    print(booked_tour_packages)
    return render_template(
        "dashboard.html",
        booked_destinations=booked_destinations,
        tour_packages=booked_tour_packages,
    )


# db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
