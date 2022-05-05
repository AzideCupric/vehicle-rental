from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

manager_bp = Blueprint("manager", __name__)


@manager_bp.route("/")
@login_required
def index():
    data_table = get_db().table("data")
    datas = data_table.all()
    return render_template("os/index.html", datas=datas)


@manager_bp.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == "POST":
        carname = request.form["carname"]
        status = request.form["status"]
        count = request.form["count"]
        error = None

        if not carname:
            error = "需要输入车辆名称"
        elif not status:
            error = "需要输入出借状态"
        elif not count:
            error = "需要输入出借次数"

        if error is not None:
            flash(error)
        else:
            data_table = get_db().table("data")
            data_table.insert({"carname": carname, "status": status, "count": count})
            return redirect(url_for("manager.index"))

    return render_template("os/add.html")
