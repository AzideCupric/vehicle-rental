from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from pytz import timezone
from tinydb import where
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

carrental_bp = Blueprint("carrental", __name__, url_prefix="/carrental")


@carrental_bp.route("/")
@login_required
def index():
    carinfo_table = get_db().table("carinfo")
    datas = carinfo_table.all()
    return render_template("os/carrental/index.html", datas=datas, pagename="租还管理")


def get_item(doc_id: int):
    item = get_db().table("carrental").get(doc_id=doc_id)

    if item is None:
        abort(404, f"不存在记录{doc_id}!")

    return item


def time_format(timestamp: int) -> str:
    dtime = datetime.fromtimestamp(timestamp, tz=timezone("Asia/Shanghai"))
    timestr = dtime.strftime("%Y-%m-%d %H:%M:%S")
    return timestr


@carrental_bp.route("/<int:doc_id>/info")
@login_required
def info(doc_id):
    items = get_item(doc_id)
    return render_template(
        "os/carrental/info.html", items=items, time_format=time_format
    )
