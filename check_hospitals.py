from app import app, db, Hospital

with app.app_context():
    print("SQLALCHEMY_DATABASE_URI =", app.config.get("SQLALCHEMY_DATABASE_URI"))
    print("Hospitals =", db.session.query(Hospital).count())
    for h in Hospital.query.order_by(Hospital.id).all():
        print(h.id, h.name)
