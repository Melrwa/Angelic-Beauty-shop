from datetime import datetime, timedelta
from random import choice, randint, uniform
from config import db, app
from models import User, Staff, Service, StaffService, Review, Transaction

def seed_data():
    with app.app_context():
        print("Clearing existing data...")
        db.session.query(Review).delete()
        db.session.query(Transaction).delete()
        db.session.query(StaffService).delete()
        db.session.query(Staff).delete()
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()

        print("Seeding users...")
        admin = User(name="Admin", username="admin", email="admin@example.com", role="admin")
        admin.password_hash = "admin123"  # Set password securely
        client1 = User(name="John Doe", username="johndoe", email="john@example.com", role="user")
        client1.password_hash = "password"
        client2 = User(name="Jane Smith", username="janesmith", email="jane@example.com", role="user")
        client2.password_hash = "password"
        users = [admin, client1, client2]
        db.session.add_all(users)
        db.session.commit()

        print("Seeding services...")
        services = [
            Service(name="Haircut", picture="haircut.jpg", price=20.0, time_taken=0.5),
            Service(name="Hair Coloring", picture="coloring.jpg", price=50.0, time_taken=1.5),
            Service(name="Massage", picture="massage.jpg", price=70.0, time_taken=1.0),
            Service(name="Facial", picture="facial.jpg", price=40.0, time_taken=1.0),
            Service(name="Manicure", picture="manicure.jpg", price=30.0, time_taken=0.75),
        ]
        db.session.add_all(services)
        db.session.commit()

        print("Seeding staff...")
        staff_members = [
            Staff(name="Alice Brown", picture="alice.jpg", gender="female"),
            Staff(name="Bob Green", picture="bob.jpg", gender="male"),
            Staff(name="Charlie Black", picture="charlie.jpg", gender="male"),
        ]
        db.session.add_all(staff_members)
        db.session.commit()

        print("Assigning staff to services...")
        staff_services = [
            StaffService(staff_id=staff_members[0].id, service_id=services[0].id),  # Alice → Haircut
            StaffService(staff_id=staff_members[0].id, service_id=services[1].id),  # Alice → Hair Coloring
            StaffService(staff_id=staff_members[1].id, service_id=services[2].id),  # Bob → Massage
            StaffService(staff_id=staff_members[2].id, service_id=services[3].id),  # Charlie → Facial
            StaffService(staff_id=staff_members[2].id, service_id=services[4].id),  # Charlie → Manicure
        ]
        db.session.add_all(staff_services)
        db.session.commit()

        print("Seeding transactions...")
        transactions = [
            Transaction(
                service_id=services[0].id,
                staff_id=staff_members[0].id,
                client_id=client1.id,
                amount_paid=services[0].price,
                time_taken=services[0].time_taken,
                booking_time=datetime.utcnow() - timedelta(days=randint(1, 10)),
                completed_at=datetime.utcnow(),
            ),
            Transaction(
                service_id=services[2].id,
                staff_id=staff_members[1].id,
                client_id=client2.id,
                amount_paid=services[2].price,
                time_taken=services[2].time_taken,
                booking_time=datetime.utcnow() - timedelta(days=randint(1, 10)),
                completed_at=datetime.utcnow(),
            ),
        ]
        db.session.add_all(transactions)
        db.session.commit()

        print("Seeding reviews...")
        reviews = [
            Review(staff_id=staff_members[0].id, client_id=client1.id, rating=4.5, review="Great haircut!"),
            Review(staff_id=staff_members[1].id, client_id=client2.id, rating=5.0, review="Best massage ever!"),
        ]
        db.session.add_all(reviews)
        db.session.commit()

        print("Database successfully seeded!")

if __name__ == "__main__":
    seed_data()
