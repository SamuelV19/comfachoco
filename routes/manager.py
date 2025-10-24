from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Request as Req, User
from datetime import datetime

manager_bp = Blueprint("manager", __name__, template_folder="../templates")

@manager_bp.route("/manager/dashboard")
@login_required
def dashboard():
    if current_user.role != "manager":
        flash("Acceso denegado: se requiere rol manager.", "error")
        return redirect(url_for("employee.dashboard"))
    pending = Req.query.filter_by(status="pending").order_by(Req.created_at.asc()).all()
    return render_template("manager/dashboard.html", user=current_user, requests=pending)

@manager_bp.route("/manager/request/<int:req_id>/approve", methods=["POST"])
@login_required
def approve(req_id):
    if current_user.role != "manager":
        flash("Acceso denegado.", "error")
        return redirect(url_for("employee.dashboard"))
    r = Req.query.get_or_404(req_id)
    if r.status != "pending":
        flash("La solicitud ya fue procesada.", "error")
        return redirect(url_for("manager.dashboard"))
    r.status = "approved"
    r.manager_id = current_user.id
    # si es vacaciones, descontar saldo
    if r.type == "vacation":
        emp = User.query.get(r.user_id)
        emp.vacation_balance_days = max(0.0, emp.vacation_balance_days - r.requested_days)
    db.session.commit()
    flash("Solicitud aprobada.", "success")
    return redirect(url_for("manager.dashboard"))

@manager_bp.route("/manager/request/<int:req_id>/reject", methods=["POST"])
@login_required
def reject(req_id):
    if current_user.role != "manager":
        flash("Acceso denegado.", "error")
        return redirect(url_for("employee.dashboard"))
    r = Req.query.get_or_404(req_id)
    if r.status != "pending":
        flash("La solicitud ya fue procesada.", "error")
        return redirect(url_for("manager.dashboard"))
    comment = request.form.get("comment", "")
    r.status = "rejected"
    r.manager_id = current_user.id
    r.manager_comment = comment
    db.session.commit()
    flash("Solicitud rechazada.", "success")
    return redirect(url_for("manager.dashboard"))
