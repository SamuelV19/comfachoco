from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Request as Req, User
from services import business_days_between
from datetime import datetime

employee_bp = Blueprint("employee", __name__, template_folder="../templates")

@employee_bp.route("/employee/dashboard")
@login_required
def dashboard():
    # only employees (or managers can also view their employee dashboard)
    reqs = Req.query.filter_by(user_id=current_user.id).order_by(Req.created_at.desc()).all()
    return render_template("employee/dashboard.html", user=current_user, requests=reqs)

@employee_bp.route("/employee/request/new", methods=["GET", "POST"])
@login_required
def new_request():
    if request.method == "POST":
        typ = request.form.get("type")
        start_str = request.form.get("start_date")
        end_str = request.form.get("end_date")
        reason = request.form.get("reason", "")
        try:
            start = datetime.fromisoformat(start_str).date()
            end = datetime.fromisoformat(end_str).date()
        except Exception:
            flash("Formato de fecha inválido. Usa YYYY-MM-DD.", "error")
            return redirect(url_for("employee.new_request"))

        days = business_days_between(start, end)
        if days <= 0:
            flash("Rango de fechas inválido o sin días hábiles.", "error")
            return redirect(url_for("employee.new_request"))

        if typ == "vacation" and current_user.vacation_balance_days < days:
            flash(f"No tienes saldo suficiente. Solicitas {days} días y tienes {current_user.vacation_balance_days}.", "error")
            return redirect(url_for("employee.new_request"))

        r = Req(user_id=current_user.id, type=typ, start_date=start, end_date=end, requested_days=days, reason=reason)
        db.session.add(r)
        db.session.commit()
        flash("Solicitud creada correctamente.", "success")
        return redirect(url_for("employee.dashboard"))

    return render_template("employee/new_request.html", user=current_user)
