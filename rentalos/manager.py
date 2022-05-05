from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from rentalos.auth import login_required
from rentalos.db import get_db
manager_bp=Blueprint('manager',__name__)

@manager_bp.route('/')
@login_required
def index():
    data_table=get_db().table('data')
    datas=data_table.all()
    return render_template("os/index.html",datas=datas)