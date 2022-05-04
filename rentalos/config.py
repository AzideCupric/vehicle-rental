import os
from flask import current_app

class config():
    
    #DB_LINK:str=os.path.join(current_app.instance_path+'db/')
    DB_LINK:str='./db/'
    
appConfig=config()