# app.py (fixed, ready for Render)
import os
from dotenv import load_dotenv

# load .env for local development only; Render ignores .env
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length

# --- CONFIG ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')

# Primary: read DATABASE_URL environment variable (production)
# Fallback behavior: if USE_LOCAL_MYSQL=1, build mysql URL from DB_* vars (local dev)
# Otherwise fallback to local sqlite file (safe on Render)
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_LOCAL_MYSQL = os.environ.get('USE_LOCAL_MYSQL', '0') == '1'

if not DATABASE_URL and USE_LOCAL_MYSQL:
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'covid_beds')
    # Use mysql+mysqlconnector dialect if using mysql-connector-python
    DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Final fallback: sqlite file in project root
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///local_dev.db'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# avoid stale connection errors on some hosts
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS ---
class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    contact = db.Column(db.String(50))
    icu_total = db.Column(db.Integer, default=0)
    oxygen_total = db.Column(db.Integer, default=0)
    normal_total = db.Column(db.Integer, default=0)
    ventilator_total = db.Column(db.Integer, default=0)
    icu_available = db.Column(db.Integer, default=0)
    oxygen_available = db.Column(db.Integer, default=0)
    normal_available = db.Column(db.Integer, default=0)
    ventilator_available = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    users = db.relationship('User', back_populates='hospital', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='hospital', lazy='dynamic')
    doctors = db.relationship('Doctor', back_populates='hospital', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('patient', 'hospital', 'admin'), default='patient')
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    hospital = db.relationship('Hospital', back_populates='users', foreign_keys=[hospital_id])


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(150))
    photo = db.Column(db.String(255))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    available = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    hospital = db.relationship('Hospital', back_populates='doctors')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    bed_type = db.Column(db.Enum('icu', 'oxygen', 'normal', 'ventilator'))
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'discharged'), default='pending')
    name = db.Column(db.String(150))
    contact = db.Column(db.String(50))
    symptoms = db.Column(db.Text)
    id_proof = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('User', foreign_keys=[patient_id])
    hospital = db.relationship('Hospital', back_populates='bookings')


class Waitlist(db.Model):
    __tablename__ = 'waitlist'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bed_type = db.Column(db.Enum('icu', 'oxygen', 'normal', 'ventilator'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    patient = db.relationship('User', foreign_keys=[patient_id])


# --- FORMS ---
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('hospital', 'Hospital'), ('admin', 'Admin')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class HospitalForm(FlaskForm):
    name = StringField('Hospital Name', validators=[DataRequired()])
    address = TextAreaField('Address')
    city = StringField('City')
    contact = StringField('Contact')
    icu_total = IntegerField('ICU beds', default=0)
    oxygen_total = IntegerField('Oxygen beds', default=0)
    normal_total = IntegerField('Normal beds', default=0)
    ventilator_total = IntegerField('Ventilator beds', default=0)
    submit = SubmitField('Save')


class BookingForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    bed_type = SelectField('Bed Type', choices=[
        ('icu', 'ICU'), ('oxygen', 'Oxygen'), ('normal', 'Normal'), ('ventilator', 'Ventilator')
    ])
    doctor_id = SelectField('Doctor (optional)', coerce=int, choices=[], validate_choice=False)
    symptoms = TextAreaField('Symptoms')
    id_proof = StringField('ID Proof (number)')
    submit = SubmitField('Book')


# --- LOGIN LOADER ---
@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


# --- HEALTH CHECK (safe, does not touch DB) ---
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "app": "hospital_bed_system"}), 200


# --- ROUTES ---
@app.route('/')
def index():
    try:
        city = request.args.get('city')
        query = Hospital.query
        if city:
            query = query.filter(Hospital.city.ilike(f"%{city}%"))
        hospitals = query.all()
        return render_template('index.html', hospitals=hospitals)
    except Exception as e:
        # Log the exception to stderr (visible in Render logs) then return a generic 500 page
        app.logger.exception("Error in index route")
        return render_template('500.html'), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Email already registered', 'warning')
            return redirect(url_for('register'))
        hashed = generate_password_hash(form.password.data)
        user = User(name=form.name.data, email=form.email.data, phone=form.phone.data, password=hashed,
                    role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


# ------------------------
# HOSPITAL ROUTES
# ------------------------
@app.route('/hospital/create', methods=['GET', 'POST'])
@login_required
def create_hospital():
    if current_user.role not in ['hospital', 'admin']:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    form = HospitalForm()
    if form.validate_on_submit():
        h = Hospital(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            contact=form.contact.data,
            icu_total=form.icu_total.data or 0,
            oxygen_total=form.oxygen_total.data or 0,
            normal_total=form.normal_total.data or 0,
            ventilator_total=form.ventilator_total.data or 0,
            icu_available=form.icu_total.data or 0,
            oxygen_available=form.oxygen_total.data or 0,
            normal_available=form.normal_total.data or 0,
            ventilator_available=form.ventilator_total.data or 0
        )
        db.session.add(h)
        db.session.commit()

        if current_user.role == 'hospital':
            current_user.hospital_id = h.id
            db.session.commit()

        flash('Hospital created', 'success')
        return redirect(url_for('index'))

    return render_template('hospital_dashboard.html', form=form)


@app.route('/hospital/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_hospital(id):
    h = Hospital.query.get_or_404(id)
    if current_user.role == 'hospital' and current_user.hospital_id != h.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    form = HospitalForm(obj=h)

    if form.validate_on_submit():
        delta_icu = (form.icu_total.data or 0) - (h.icu_total or 0)
        h.icu_total = form.icu_total.data or 0
        h.icu_available = max(0, (h.icu_available or 0) + delta_icu)

        delta_oxygen = (form.oxygen_total.data or 0) - (h.oxygen_total or 0)
        h.oxygen_total = form.oxygen_total.data or 0
        h.oxygen_available = max(0, (h.oxygen_available or 0) + delta_oxygen)

        delta_normal = (form.normal_total.data or 0) - (h.normal_total or 0)
        h.normal_total = form.normal_total.data or 0
        h.normal_available = max(0, (h.normal_available or 0) + delta_normal)

        delta_vent = (form.ventilator_total.data or 0) - (h.ventilator_total or 0)
        h.ventilator_total = form.ventilator_total.data or 0
        h.ventilator_available = max(0, (h.ventilator_available or 0) + delta_vent)

        h.name = form.name.data
        h.address = form.address.data
        h.city = form.city.data
        h.contact = form.contact.data

        db.session.commit()
        flash('Hospital updated', 'success')
        return redirect(url_for('index'))

    return render_template('hospital_dashboard.html', form=form, hospital=h)


@app.route('/hospitals')
def hospitals():
    city = request.args.get('city')
    q = Hospital.query
    if city:
        q = q.filter(Hospital.city.ilike(f"%{city}%"))
    return render_template('hospitals.html', hospitals=q.all())


@app.route('/hospital/<int:id>/beds')
def hospital_beds(id):
    h = Hospital.query.get_or_404(id)
    return render_template('hospital_beds.html', hospital=h)


# -------------------------------------------------------------------
# NEW API ROUTE FOR REALTIME BED AVAILABILITY
# -------------------------------------------------------------------
@app.route('/api/hospital/<int:id>/availability')
def api_availability(id):
    h = Hospital.query.get(id)
    if not h:
        return jsonify({'error': 'hospital not found'}), 404

    return jsonify({
        'id': h.id,
        'name': h.name,
        'icu': h.icu_available or 0,
        'oxygen': h.oxygen_available or 0,
        'normal': h.normal_available or 0,
        'ventilator': h.ventilator_available or 0
    })


# ------------------------
# BOOKING ROUTES
# ------------------------
@app.route('/book/<int:hospital_id>', methods=['GET', 'POST'])
@login_required
def book(hospital_id):
    h = Hospital.query.get_or_404(hospital_id)
    form = BookingForm()

    docs = Doctor.query.filter_by(hospital_id=h.id).order_by(Doctor.name).all()

    choices = [(0, 'No preference')]
    for d in docs:
        avail_text = 'Available' if (d.available or 0) > 0 else 'Unavailable'
        label = f"{d.name} — {d.specialization or 'Doctor'} | {d.experience or 0} yrs | Age {d.age or '-'} | {avail_text}"
        choices.append((d.id, label))

    form.doctor_id.choices = choices

    if form.validate_on_submit():
        at_field = f"{form.bed_type.data}_available"
        bed_available = getattr(h, at_field, 0)

        if bed_available <= 0:
            flash('No beds available of that type.', 'warning')
            return redirect(url_for('book', hospital_id=h.id))

        selected_doc_id = form.doctor_id.data
        chosen_doctor = None

        if selected_doc_id and selected_doc_id != 0:
            chosen_doctor = Doctor.query.get(selected_doc_id)

            if not chosen_doctor or chosen_doctor.hospital_id != h.id:
                flash('Invalid doctor.', 'danger')
                return redirect(url_for('book', hospital_id=h.id))

            if (chosen_doctor.available or 0) <= 0:
                flash('Doctor unavailable.', 'danger')
                return redirect(url_for('book', hospital_id=h.id))

        b = Booking(
            patient_id=current_user.id,
            hospital_id=h.id,
            bed_type=form.bed_type.data,
            status='confirmed',
            name=form.name.data,
            contact=form.contact.data,
            symptoms=form.symptoms.data,
            id_proof=form.id_proof.data
        )

        setattr(h, at_field, bed_available - 1)

        if chosen_doctor:
            chosen_doctor.available -= 1
            db.session.add(chosen_doctor)

        db.session.add(b)
        db.session.commit()

        flash('Booking Confirmed', 'success')
        return redirect(url_for('booking_success', booking_id=b.id))

    return render_template('book.html', form=form, hospital=h, doctors=docs)


@app.route('/booking/success/<int:booking_id>')
@login_required
def booking_success(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if current_user.role == 'patient' and b.patient_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('index'))
    return render_template('booking_success.html', booking=b)


@app.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(patient_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)


# --- START SERVER (local only) ---
if __name__ == '__main__':
    # create local DB tables when running the script locally
    with app.app_context():
        db.create_all()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

