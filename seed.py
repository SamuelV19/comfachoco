from app import create_app
from models import db, User
import os

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    juan = User(username="juan", full_name="Juan Pérez", role="employee", vacation_balance_days=12.5)
    juan.set_password("1234")
    maria = User(username="maria", full_name="María Gómez", role="manager", vacation_balance_days=20.0)
    maria.set_password("1234")
    admin = User(username="admin", full_name="Admin", role="admin", vacation_balance_days=30.0)
    admin.set_password("admin")

    db.session.add_all([juan, maria, admin])
    db.session.commit()

    print("Seed creado: usuarios -> juan (pwd 1234), maria (pwd 1234), admin (pwd admin)")
    print("DB en:", os.path.abspath("app.db"))
