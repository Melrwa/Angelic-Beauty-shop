from flask import jsonify
from flask_restful import Resource
from datetime import datetime, timedelta
from models import db, Transaction, Staff, Service

class ReportsResource(Resource):
    def get(self):
        now = datetime.utcnow()

        try:
            # Daily revenue
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_revenue = (
                db.session.query(db.func.sum(Transaction.amount_paid))
                .filter(Transaction.booking_time >= start_of_day)
                .scalar() or 0
            )

            # Weekly revenue
            start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
            weekly_revenue = (
                db.session.query(db.func.sum(Transaction.amount_paid))
                .filter(Transaction.booking_time >= start_of_week)
                .scalar() or 0
            )

            # Monthly revenue
            start_of_month = start_of_day.replace(day=1)
            monthly_revenue = (
                db.session.query(db.func.sum(Transaction.amount_paid))
                .filter(Transaction.booking_time >= start_of_month)
                .scalar() or 0
            )

            # Most booked staff (Ensure consistent JSON structure)
            most_booked_staff = (
                db.session.query(Staff.name, db.func.count(Transaction.id))
                .join(Transaction)
                .group_by(Staff.id)
                .order_by(db.func.count(Transaction.id).desc())
                .limit(3)
                .all()
            )
            most_booked_staff = [
                {"name": staff[0], "transactionCount": staff[1]} for staff in most_booked_staff
            ]

            # Most booked service (Ensure consistent JSON structure)
            most_booked_service = (
                db.session.query(Service.name, db.func.count(Transaction.id))
                .join(Transaction)
                .group_by(Service.id)
                .order_by(db.func.count(Transaction.id).desc())
                .limit(3)
                .all()
            )
            most_booked_service = [
                {"name": service[0], "transactionCount": service[1]} for service in most_booked_service
            ]

            return jsonify({
                "dailyRevenue": daily_revenue,
                "weeklyRevenue": weekly_revenue,
                "monthlyRevenue": monthly_revenue,
                "mostBookedStaff": most_booked_staff,  # Corrected key
                "mostBookedService": most_booked_service  # Corrected key
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

    def get(self):
        now = datetime.utcnow()

        try:
            # Get total services & staff count
            total_services = db.session.query(Service).count()
            total_staff = db.session.query(Staff).count()

            # Daily revenue calculation
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_revenue = (
                db.session.query(db.func.sum(Transaction.amount_paid))
                .filter(Transaction.booking_time >= start_of_day)
                .scalar() or 0
            )

            return jsonify({
                "total_services": total_services,
                "total_staff": total_staff,
                "daily_revenue": daily_revenue
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
