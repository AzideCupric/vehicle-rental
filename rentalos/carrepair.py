import uuid
from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from pytz import timezone
from tinydb.operations import set
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

carrepair_bp = Blueprint("carrepair", __name__, url_prefix="/carrepair")


def get_items(doc_id: int):
    table = get_db().table("carinfo")
    raw_item = table.get(doc_id=doc_id)

    if raw_item is None:
        abort(404, f"不存在记录{doc_id}!")
    else:
        item = {}
        try:
            item = raw_item["repair"]
        except KeyError:
            table.update({"repair": {}}, doc_ids=[doc_id])
    return item


def time_format2str(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    # dtime = datetime.strptime(time, '%Y-%m-%dT%H:%M')
    timestr = dtime.strftime("%Y-%m-%d %H:%M")
    return timestr


@carrepair_bp.route("/<int:doc_id>/info")
@login_required
def info(doc_id):
    items = get_items(doc_id)
    sorted_items = sorted(items.items(), key=lambda x: x[1]["time"])
    return render_template(
        "os/carrepair/info.html",
        items=sorted_items,
        doc_id=doc_id,
        time_format=time_format2str,
    )


def time_format2stamp(timestr: str) -> int:
    dtime = datetime.strptime(timestr, "%Y-%m-%dT%H:%M")
    return int(dtime.timestamp())


@carrepair_bp.route("/<int:doc_id>/add", methods=["GET", "POST"])
@login_required
def add(doc_id):
    if request.method == "POST":
        place = request.form["place"]
        time = time_format2stamp(request.form["time"])
        cost = request.form["cost"]
        error = None

        if not place:
            error = "需要输入维修地点"
        elif not time:
            error = "需要输入维修时间"
        elif not cost:
            error = "需要输入维修费用"

        if error is None:
            table = get_db().table("carinfo")
            try:
                items: dict = get_items(doc_id)
                for idx, item in enumerate(items.values(), start=1):
                    if item["time"] and abs(item["time"] - time) <= 15 * 60:
                        raise LookupError(idx)
            except LookupError as e:
                idx = e.args[0]
                error = f"该维修时间与第{idx}条过近"
            else:
                new_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, str(time))
                new_item = {str(new_uuid): {"place": place, "time": time, "cost": cost}}
                items.update(new_item)
                table.update(set("repair", items), doc_ids=[doc_id])
                table.update(set("repair_count", len(items)), doc_ids=[doc_id])
                return redirect(url_for("carrepair.info", doc_id=doc_id))

        flash(error)

    return render_template("os/carrepair/add.html", doc_id=doc_id)


def time_format2form(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    timestr = dtime.strftime("%Y-%m-%dT%H:%M")
    return timestr


@carrepair_bp.route("/<int:doc_id>/update/<string:repair_id>", methods=["GET", "POST"])
@login_required
def update(doc_id, repair_id):
    items: dict[str, dict] = get_items(doc_id)
    if request.method == "POST":
        place = request.form["place"]
        time = time_format2stamp(request.form["time"])
        cost = request.form["cost"]
        error = None

        if not place:
            error = "需要输入维修地点"
        elif not time:
            error = "需要输入维修时间"
        elif not cost:
            error = "需要输入维修费用"

        if error is None:
            table = get_db().table("carinfo")
            try:
                extract_items = items.copy()
                extract_items.pop(repair_id)
                for idx, item in enumerate(extract_items.values(), start=1):
                    if item["time"] and abs(item["time"] - time) <= 15 * 60:
                        raise LookupError(idx)
            except LookupError as e:
                idx = e.args[0]
                error = f"该维修时间与第{idx}条过近"
            else:
                items[repair_id].update(place=place, time=time, cost=cost)
                table.update(set("repair", items), doc_ids=[doc_id])
                return redirect(url_for("carrepair.info", doc_id=doc_id))

        flash(error)

    return render_template(
        "os/carrepair/update.html",
        doc_id=doc_id,
        item=items[repair_id],
        time_format2form=time_format2form,
    )


@carrepair_bp.route("/<int:doc_id>/delete/<string:repair_id>", methods=["GET", "POST"])
@login_required
def delete(doc_id, repair_id):
    table = get_db().table("carinfo")
    items: dict = get_items(doc_id)
    items.pop(repair_id)
    table.update(set("repair", items), doc_ids=[doc_id])
    table.update(set("repair_count", len(items)), doc_ids=[doc_id])
    return redirect(url_for("carrepair.info", doc_id=doc_id))
