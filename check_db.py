# check_db.py
from app import app
from app import db
from app import Hospital

with app.app_context():
    print("SQLALCHEMY_DATABASE_URI =", app.config.get('SQLALCHEMY_DATABASE_URI'))
    try:
        count = Hospital.query.count()
        print("Hospital count:", count)
        for h in Hospital.query.order_by(Hospital.id).all():
            print(h.id, "-", h.name)
    except Exception as e:
        print("Error querying hospitals:", e)