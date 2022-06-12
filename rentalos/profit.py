import uuid
from datetime import datetime
from itertools import zip_longest

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from pytz import timezone
from tinydb.operations import set
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db

profit_bp = Blueprint("profit", __name__, url_prefix="/profit")


class Car:
    type: str
    platenum: str
    rental_cost: int
    rental_count: 0 = int
    repair_cost: int
    repair_count: int

    def __init__(
        self,
        type,
        platenum,
    ):
        self.type = type
        self.platenum = platenum
        self.rental_count = 0
        self.repair_count = 0
        self.rental_cost = 0
        self.repair_cost = 0


@profit_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    car_list: list[Car] = []
    for data in get_db().table("carinfo").all():
        new_car = Car(data["carname"], data["platenum"])

        rental_count = 0
        repair_count = 0

        rentals = data["rental"]
        repairs = data["repair"]
        for rtc, rpc in zip_longest(rentals.values(), repairs.values()):
            if rtc:
                new_car.rental_cost += int(rtc["cost"])
                rental_count += 1
            if rpc:
                new_car.repair_cost += int(rpc["cost"])
                repair_count += 1

        new_car.rental_count = rental_count
        new_car.repair_count = repair_count
        car_list.append(new_car)

    return render_template("os/profit/index.html", car_list=car_list)
