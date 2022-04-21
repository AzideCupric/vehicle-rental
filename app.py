from flask import Flask, redirect, render_template, url_for, request,g

app = Flask(__name__)


@app.route('/')
def index():
    login_url = url_for('login')
    return redirect(login_url)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('loginuser')
    passwd = request.form.get('loginpwd')
    if username and passwd:
        return redirect('/manager')
    else:
        return render_template('login.html', msg='用户名和密码不能为空')


@app.route('/register/')
def register():
    return '施工中'


@app.route('/forgot/')
def forgot():
    return '施工中'


@app.route('/manager/')
def manager():
    return '<h1>Login OK</h1>'
