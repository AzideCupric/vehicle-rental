import functools
from flask import Blueprint,flash,g,redirect,render_template,request,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from rentalos.db import get_db

auth_bp=Blueprint('auth',__name__,url_prefix='/auth')