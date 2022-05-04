from tinydb import TinyDB

import click
from flask import g, current_app, Flask
from flask.cli import with_appcontext


def get_db() -> TinyDB:
    '''向flask全局变量中添加数据库'''
    if 'db' not in g:
        g.db = TinyDB(current_app.config['DATABASE'])

    return g.db


def close_db(e=None):
    '''关闭全局数据库'''
    db: TinyDB = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Clear the existing data and create new tables."""
    db = get_db()
    db.truncate()
    db.table('user')
    db.table('os')


@click.command('init-db')  # 创建一个命令行命令
@with_appcontext
def init_db_command():
    """清空旧数据，创建空的新表"""
    init_db()
    click.echo(' * Init-db: 数据库初始化终了...')


def init_app(app: Flask):
    '''在flask应用中注册函数'''
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
