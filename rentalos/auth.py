import functools
from textwrap import indent
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from rentalos.db import get_db
from tinydb import where

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '请输入用户名！'
        elif not password:
            error = '请输入密码！'

        if error is None:
            try:
                auth_table = db.table('user')
                if not auth_table.get(where('username') == username):
                    userdata = {
                        'username': username,
                        'password': generate_password_hash(password)
                    }
                    auth_table.insert(userdata)
                else:
                    raise LookupError('username existed')
            except LookupError:
                error = f'用户:{username} 已经存在！'
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth_table = get_db().table('user')
        error = None
        user = auth_table.get(where('username') == username)

        if user is None:
            error = f'该用户名:{username}不存在'
        elif not check_password_hash(user['password'], password):
            error = '该密码与用户名不匹配'

        if error is None:
            session.clear()
            session['user_doc_id'] = user.doc_id
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')


@auth_bp.before_app_request
def load_logged_in_user():
    user_doc_id = session.get('user_doc_id')

    if user_doc_id is None:
        g.user = None
    else:
        g.user = get_db().get(doc_id=user_doc_id)


@auth_bp.route('/exit')
def exit():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect('auth.login')
        return view(**kwargs)

    return wrapped_view
