# seed.py
from werkzeug.security import generate_password_hash
from app import app, db, User, Hospital

def seed():
    with app.app_context():
        # admin user
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                name='Admin User',
                email='admin@example.com',
                phone='9999999999',
                password=generate_password_hash('adminpass'),
                role='admin'
            )
            db.session.add(admin)
            print("Admin user added: admin@example.com / adminpass")
        else:
            print("Admin already exists")

        # sample hospital
        if not Hospital.query.filter_by(name='City Care Hospital').first():
            h = Hospital(
                name='City Care Hospital',
                address='123 Main St',
                city='YourCity',
                contact='0123456789',
                icu_total=5, oxygen_total=10, normal_total=25, ventilator_total=2,
                icu_available=5, oxygen_available=10, normal_available=25, ventilator_available=2
            )
            db.session.add(h)
            print("Sample hospital added: City Care Hospital")
        else:
            print("Sample hospital already exists")

        db.session.commit()
        print("Seed complete")

if __name__ == '__main__':
    seed()
