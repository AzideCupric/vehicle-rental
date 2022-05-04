import os
from flask import Flask
from .config import appConfig

def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    app.config.update(SECRET_KEY='dev')
    if test_config is None:
        app.config.from_object(appConfig,silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    @app.route('/')
    def hello():
        return 'Hello,World'
    
    return app