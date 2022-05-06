from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

manager_bp = Blueprint("manager", __name__)


@manager_bp.route("/")
@login_required
def index():
    carinfo_table = get_db().table("carinfo")
    datas = carinfo_table.all()
    return render_template("os/index.html", datas=datas, pagename="车辆管理")


@manager_bp.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == "POST":
        carname = request.form["carname"]
        status = request.form["status"]
        platenum = request.form["platenum"]
        count = request.form["count"]
        error = None

        if not carname:
            error = "需要输入车辆名称"
        elif not status:
            error = "需要输入出借状态"
        elif not platenum:
            error = "需要输入车牌号"
        elif not count:
            error = "需要输入出借次数"

        if error is not None:
            flash(error)
        else:
            data_table = get_db().table("carinfo")
            data_table.insert(
                {
                    "carname": carname,
                    "status": status,
                    "platenum": platenum,
                    "count": count,
                }
            )
            return redirect(url_for("manager.index"))

    return render_template("os/add.html")


def get_item(doc_id: int, type: str):
    item = get_db().table(type).get(doc_id=doc_id)
    if item is None:
        abort(404, f"不存在记录{doc_id}!")

    return item


@manager_bp.route("/<str:type>/<int:doc_id>/update", methods=("GET", "POST"))
@login_required
def update(doc_id, type):
    item = get_item(doc_id, type)
    if request.method == "POST":

        if type == "carinfo":
            carname = request.form["carname"]
            status = request.form["status"]
            platenum = request.form["platenum"]
            count = request.form["count"]
            error = None

            if not carname:
                error = "需要输入车辆名称"
            elif not status:
                error = "需要输入出借状态"
            elif not platenum:
                error = "需要输入车牌号"
            elif not count:
                error = "需要输入出借次数"

            if error is not None:
                flash(error)
            else:
                data_table = get_db().table(type)
                data_table.update(
                    {
                        "carname": carname,
                        "status": status,
                        "platenum": platenum,
                        "count": count,
                    },
                    doc_ids=[doc_id],
                )
                return redirect(url_for("manager.index"))

        else:
            pass

        return render_template("os/update.html", item=item)
