from tinydb import TinyDB
from flask import g,current_app

def get_db(dbname) -> TinyDB:
    if f'db_{dbname}' not in g:
        g[f'db_{dbname}']=TinyDB(current_app.config['DB_LINK']+f'{dbname}.json')
    return g[f'db_{dbname}']

def close_db(dbname):
    db:TinyDB=g.pop(f'db_{dbname}',None)
    if db is not None:
        db.close()