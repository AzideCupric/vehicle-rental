import os

from flask import Flask, redirect, render_template, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "rentalos.json")
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import auth, carinfo, carrental, carrepair

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(carinfo.carinfo_bp)
    app.register_blueprint(carrental.carrental_bp)
    app.register_blueprint(carrepair.carrepair_bp)
    app.add_url_rule("/", endpoint="carinfo.index")

    @app.route("/hello/")
    def hello():
        return render_template("os/hello.html")

    return app
