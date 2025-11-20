# seed_hospitals.py
from app import db, Hospital, app
with app.app_context():
    db.session.query(Hospital).delete()  # optional: clear existing
    hospitals = [
        ("STAR Hospital","123 Star Rd","Pune","+91-20-12345678",5,10,20,2),
        ("Apollo General","45 Apollo Ave","Pune","+91-20-87654321",3,8,15,1),
        ("City Care","12 City St","Pune","+91-20-11112222",2,5,10,0),
        ("Green Valley Hospital","9 Green Ln","Pune","+91-20-33334444",4,6,12,1),
        ("Oceanview Clinic","77 Sea Blvd","Pune","+91-20-55556666",1,3,6,0),
        ("Sunrise Health","101 Sunrise Dr","Pune","+91-20-77778888",6,12,25,3)
    ]
    for n,a,c,tel,icu,oxy,nor,vent in hospitals:
        h = Hospital(
            name=n,address=a,city=c,contact=tel,
            icu_total=icu,oxygen_total=oxy,normal_total=nor,ventilator_total=vent,
            icu_available=icu,oxygen_available=oxy,normal_available=nor,ventilator_available=vent
        )
        db.session.add(h)
    db.session.commit()
    print("6 hospitals inserted")
