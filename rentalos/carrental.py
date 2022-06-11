from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from pytz import timezone
from tinydb import where
from tinydb.operations import set
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

carrental_bp = Blueprint("carrental", __name__, url_prefix="/carrental")


def get_item(doc_id: int):
    raw_item = get_db().table("carinfo").get(doc_id=doc_id)

    if raw_item is None:
        abort(404, f"不存在记录{doc_id}!")
    else:
        item = raw_item["rental"]

    return item


def time_format2str(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    # dtime = datetime.strptime(time, '%Y-%m-%dT%H:%M')
    timestr = dtime.strftime("%Y-%m-%d %H:%M")
    return timestr


@carrental_bp.route("/<int:doc_id>/info")
@login_required
def info(doc_id):
    items = get_item(doc_id)
    return render_template(
        "os/carrental/info.html",
        items=items,
        doc_id=doc_id,
        time_format=time_format2str,
    )


def time_format2stamp(timestr: str) -> int:
    dtime = datetime.strptime(timestr, "%Y-%m-%dT%H:%M")
    return int(dtime.timestamp())


@carrental_bp.route("/<int:doc_id>/add", methods=("GET", "POST"))
@login_required
def add(doc_id):
    if request.method == "POST":
        user = request.form["user"]
        starttime = time_format2stamp(request.form["start"])
        stoptime = time_format2stamp(request.form["stop"])
        cost = request.form["cost"]
        error = None

        if not user:
            error = "需要输入租车人姓名"
        elif not starttime:
            error = "需要输入租车时间"
        elif not stoptime:
            error = "需要输入还车时间"
        elif not cost:
            error = "需要输入租金"

        if error is None:
            table = get_db().table("carinfo")
            try:
                items: dict = table.get(doc_id=doc_id)["rental"]
                for idx, item in enumerate(items.values()):
                    if (
                        item["start"] <= starttime < item["stop"]
                        or item["start"] <= stoptime < item["stop"]
                        or starttime <= item["start"] < stoptime
                        or starttime <= item["stop"] < stoptime
                    ):
                        raise LookupError(idx)
            except LookupError as e:
                idx = e.args[0]
                error = f"当前时间与已有的第{idx}条记录冲突"
            else:
                new_item = {
                    (len(items) + 1): {
                        "user": user,
                        "start": starttime,
                        "stop": stoptime,
                        "cost": cost,
                    }
                }
                items.update(new_item)
                table.update(set("rental", items), doc_ids=[doc_id])
                return redirect(url_for("carrental.info", doc_id=doc_id))

        flash(error)

    return render_template("os/carrental/add.html")
