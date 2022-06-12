import uuid
from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from pytz import timezone
from tinydb import where
from tinydb.operations import set
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

carrental_bp = Blueprint("carrental", __name__, url_prefix="/carrental")


def get_items(doc_id: int):
    table = get_db().table("carinfo")
    raw_item = table.get(doc_id=doc_id)

    if raw_item is None:
        abort(404, f"不存在记录{doc_id}!")
    else:
        item = {}
        try:
            item = raw_item["rental"]
        except KeyError:
            table.update({"rental": {}}, doc_ids=[doc_id])
    return item


def time_format2str(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    # dtime = datetime.strptime(time, '%Y-%m-%dT%H:%M')
    timestr = dtime.strftime("%Y-%m-%d %H:%M")
    return timestr


@carrental_bp.route("/<int:doc_id>/info")
@login_required
def info(doc_id):
    items = get_items(doc_id)
    sorted_items = sorted(items.items(), key=lambda x: x[1]["start"])
    return render_template(
        "os/carrental/info.html",
        items=sorted_items,
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
        elif starttime >= stoptime:
            error = "租车时间需要小于还车时间"

        if error is None:
            table = get_db().table("carinfo")
            try:
                items: dict = get_items(doc_id)
                for idx, item in enumerate(items.values(), start=1):
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
                new_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, str(starttime))
                new_item = {
                    str(new_uuid): {
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

    return render_template("os/carrental/add.html", doc_id=doc_id)


def time_format2form(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    timestr = dtime.strftime("%Y-%m-%dT%H:%M")
    return timestr


@carrental_bp.route("/<int:doc_id>/update/<string:rental_id>", methods=["GET", "POST"])
@login_required
def update(doc_id, rental_id):
    items: dict[str, dict] = get_items(doc_id)
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
        elif starttime >= stoptime:
            error = "租车时间需要小于还车时间"

        if error is None:
            table = get_db().table("carinfo")
            try:
                extract_items = items.copy()
                extract_items.pop(rental_id)
                for idx, item in enumerate(extract_items.values(), start=1):
                    if (
                        item["start"] <= starttime < item["stop"]
                        or item["start"] <= stoptime < item["stop"]
                        or starttime <= item["start"] < stoptime
                        or starttime <= item["stop"] < stoptime
                    ):
                        raise LookupError(idx)
            except LookupError as e:
                idx = e.args[0]
                error = f"当前时间与除该条外的第{idx}条记录冲突"
            else:
                items[rental_id].update(
                    user=user, start=starttime, stop=stoptime, cost=cost
                )
                table.update(set("rental", items), doc_ids=[doc_id])
                return redirect(url_for("carrental.info", doc_id=doc_id))

        flash(error)

    return render_template(
        "os/carrental/update.html",
        doc_id=doc_id,
        item=items[rental_id],
        time_format2form=time_format2form,
    )


@carrental_bp.route("/<int:doc_id>/delete/<string:rental_id>", methods=["GET", "POST"])
@login_required
def delete(doc_id, rental_id):
    table = get_db().table("carinfo")
    items: dict = get_items(doc_id)
    items.pop(rental_id)
    table.update(set("rental", items), doc_ids=[doc_id])
    return redirect(url_for("carrental.info", doc_id=doc_id))
