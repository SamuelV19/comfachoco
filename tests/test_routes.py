import pytest
from app import create_app
from models import db, User, Request as Req
from datetime import date

@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        e = User(username="e", full_name="Empleado", role="employee", vacation_balance_days=10)
        e.set_password("123")
        m = User(username="m", full_name="Manager", role="manager")
        m.set_password("123")
        db.session.add_all([e, m])
        db.session.commit()

    with app.test_client() as client:
        yield client

def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)

def test_login_and_access_dashboard(client):
    rv = login(client, "e", "123")
    assert b"Bienvenido" in rv.data or b"Hola" in rv.data

    rv2 = client.get("/employee/dashboard")
    assert rv2.status_code in (200,302)

def test_manager_approve_flow(client):
    login(client, "e", "123")
    resp = client.post("/employee/request/new", data={
        "type": "vacation",
        "start_date": "2025-10-20",
        "end_date": "2025-10-21",
        "reason": "Test"
    }, follow_redirects=True)
    assert b"Solicitud creada" in resp.data

    client.get("/logout", follow_redirects=True)
    login(client, "m", "123")

    rv = client.get("/manager/dashboard")
    assert rv.status_code == 200
    with client.application.app_context():
        r = Req.query.first()
        assert r is not None
        resp2 = client.post(f"/manager/request/{r.id}/approve", follow_redirects=True)
        assert b"Solicitud aprobada" in resp2.data
