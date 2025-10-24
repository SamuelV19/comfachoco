from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from config import Config
from models import db, User, Request as Req
from auth import init_login
from routes.employee import employee_bp
from routes.manager import manager_bp
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import io, csv
import os

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)
    init_login(app)

    app.register_blueprint(employee_bp)
    app.register_blueprint(manager_bp)

    @app.before_request
    def create_tables_once():
        if not hasattr(app, "_tables_created"):
            with app.app_context():
                db.create_all()
        app._tables_created = True


    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "manager":
                return redirect(url_for("manager.dashboard"))
            return redirect(url_for("employee.dashboard"))
        return redirect(url_for("auth_login"))

    @app.route("/login", methods=["GET", "POST"])
    def auth_login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Bienvenido {user.full_name or user.username}", "success")
                return redirect(url_for("index"))
            flash("Credenciales inválidas", "error")
            return redirect(url_for("auth_login"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def auth_logout():
        logout_user()
        flash("Sesión cerrada.", "success")
        return redirect(url_for("auth_login"))

    @app.route("/export/history.csv")
    @login_required
    def export_history():
        if current_user.role == "manager":
            rows = Req.query.order_by(Req.created_at.desc()).all()
        else:
            rows = Req.query.filter_by(user_id=current_user.id).order_by(Req.created_at.desc()).all()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['id','user','type','start_date','end_date','days','status','manager','manager_comment','created_at'])
        for r in rows:
            manager_name = r.manager.full_name if r.manager else ''
            cw.writerow([r.id, r.user.full_name, r.type, r.start_date.isoformat(), r.end_date.isoformat(), r.requested_days, r.status, manager_name, r.manager_comment or '', r.created_at.isoformat()])
        mem = io.BytesIO()
        mem.write(si.getvalue().encode('utf-8'))
        mem.seek(0)
        return send_file(mem, download_name="history.csv", as_attachment=True, mimetype="text/csv")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
