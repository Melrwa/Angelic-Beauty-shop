from config import db, app
from models import User, Staff, Service, StaffService, Review, Transaction
from datetime import datetime


def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Seeding Users...")
        users = [
            User(
                name="Alice Johnson",
                username="alicej",
                email="alice@example.com",
                password_hash="password123",
                gender="female",
                role="user"
            ),
            User(
                name="Bob Smith",
                username="bobsmith",
                email="bob@example.com",
                password_hash="securepass",
                gender="male",
                role="user"
            ),
            User(
                name="Admin User",
                username="admin",
                email="admin@example.com",
                password_hash="adminpass",
                gender="other",
                role="admin"
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

        print("Seeding Staff...")
        staff_members = [
            Staff(name="Mike Barber", gender="male", role="barber"),
            Staff(name="Lisa Stylist", gender="female", role="stylist"),
            Staff(name="John Spa Therapist", gender="male", role="spa_therapist"),
            Staff(name="Emma Hairdresser", gender="female", role="stylist"),
        ]
        db.session.add_all(staff_members)
        db.session.commit()

        print("Seeding Services...")
        services = [
            Service(name="Men's Haircut", price=20.0, time_taken=0.5),
            Service(name="Women's Haircut", price=30.0, time_taken=1.0),
            Service(name="Massage Therapy", price=50.0, time_taken=1.5),
            Service(name="Braiding", price=40.0, time_taken=2.0),
        ]
        db.session.add_all(services)
        db.session.commit()

        print("Associating Staff with Services...")
        staff_service_mappings = [
            StaffService(staff_id=staff_members[0].id, service_id=services[0].id),  # Mike - Men's Haircut
            StaffService(staff_id=staff_members[1].id, service_id=services[1].id),  # Lisa - Women's Haircut
            StaffService(staff_id=staff_members[2].id, service_id=services[2].id),  # John - Massage Therapy
            StaffService(staff_id=staff_members[3].id, service_id=services[3].id),  # Emma - Braiding
        ]
        db.session.add_all(staff_service_mappings)
        db.session.commit()

        print("Seeding Reviews...")
        reviews = [
            Review(staff_id=staff_members[0].id, client_id=users[0].id, rating=4.5, review="Great haircut!"),
            Review(staff_id=staff_members[1].id, client_id=users[1].id, rating=5.0, review="Loved the style!"),
            Review(staff_id=staff_members[2].id, client_id=users[0].id, rating=4.0, review="Very relaxing massage."),
            Review(staff_id=staff_members[3].id, client_id=users[1].id, rating=3.5, review="Good, but took too long."),
        ]
        db.session.add_all(reviews)
        db.session.commit()

        print("Seeding Transactions...")


        transactions = [
            # Transaction with a registered client
            Transaction(
                service_id=services[0].id,
                staff_id=staff_members[0].id,
                client_id=users[0].id,  # Registered client
                client_name=users[0].name,  # Store name for consistency
                amount_paid=services[0].price,  # Ensure this matches service price
                time_taken=services[0].time_taken,
                booking_time=datetime.utcnow(),
            ),
            
            # Transaction with an unregistered client
            Transaction(
                service_id=services[2].id,
                staff_id=staff_members[2].id,
                client_id=None,  # No client ID (unregistered)
                client_name="John Doe",  # Unregistered client, so manually entered
                amount_paid=services[2].price,  # Ensure this matches service price
                time_taken=services[2].time_taken,
                booking_time=datetime.utcnow(),
            ),
        ]

        db.session.add_all(transactions)
        db.session.commit()

        print("Seeding Complete!")

if __name__ == "__main__":
    seed_data()
