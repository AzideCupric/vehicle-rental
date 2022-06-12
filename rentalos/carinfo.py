from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from tinydb import where
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

carinfo_bp = Blueprint("carinfo", __name__, url_prefix="/carinfo")


@carinfo_bp.route("/")
@login_required
def index():
    carinfo_table = get_db().table("carinfo")
    datas = carinfo_table.all()
    return render_template("os/carinfo/index.html", datas=datas, pagename="车辆管理")


@carinfo_bp.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == "POST":
        carname = request.form["carname"]
        status = request.form["status"]
        platenum = request.form["platenum"]
        error = None

        if not carname:
            error = "需要输入车辆名称"
        elif not status:
            error = "需要输入出借状态"
        elif not platenum:
            error = "需要输入车牌号"

        if error is None:
            try:
                data_table = get_db().table("carinfo")
                if not data_table.get(where("platenum") == platenum):
                    data_table.insert(
                        {"carname": carname, "status": status, "platenum": platenum}
                    )
                else:
                    raise LookupError("data existed!")
            except LookupError:
                error = "该车牌已存在！"
            else:
                return redirect(url_for("carinfo.index"))

        flash(error)

    return render_template("os/carinfo/add.html")


def get_item(doc_id: int):
    item = get_db().table("carinfo").get(doc_id=doc_id)
    if item is None:
        abort(404, f"不存在记录{doc_id}!")

    return item


@carinfo_bp.route("/<int:doc_id>/update", methods=("GET", "POST"))
@login_required
def update(doc_id):
    item = get_item(doc_id)
    if request.method == "POST":

        carname = request.form["carname"]
        status = request.form["status"]
        platenum = request.form["platenum"]
        error = None

        if not carname:
            error = "需要输入车辆名称"
        elif not status:
            error = "需要输入出借状态"
        elif not platenum:
            error = "需要输入车牌号"

        if error is not None:
            flash(error)
        else:
            data_table = get_db().table("carinfo")
            data_table.update(
                {"carname": carname, "status": status, "platenum": platenum},
                doc_ids=[doc_id],
            )
            return redirect(url_for("carinfo.index"))

    return render_template("os/carinfo/update.html", item=item)


@carinfo_bp.route("/<int:doc_id>/delete", methods=["GET", "POST"])
@login_required
def delete(doc_id):
    item = get_item(doc_id)
    db = get_db().table("carinfo")
    db.remove(doc_ids=[item.doc_id])
    return redirect(url_for("carinfo.index"))
