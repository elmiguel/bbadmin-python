from flask import Flask
# from flask.ext.cors.extension import CORS
from flask_cors import CORS
# from flask.ext.login import LoginManager
from flask_login import LoginManager
# from flask.ext.loopback.flask_loopback import FlaskLoopback
from flask_loopback import FlaskLoopback
# from flask.ext.restless.manager import APIManager
from flask_restless import APIManager
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import Authorization
from bba_config import SECRET_KEY
from bbadmintool import BbAdminTool


app = Flask(__name__, static_url_path='/static')
app.config.from_object('bba_config')
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)
bb = BbAdminTool(app)

login_manager = LoginManager()
login_manager.init_app(app)

cors = CORS(app, allow_headers=[Authorization])


loopback = FlaskLoopback(app)

from views import *
from models import *

api_manager = APIManager(app,
                         flask_sqlalchemy_db=db,
                         preprocessors=dict(
                                            # GET=[auth_func], GET_SINGLE=[auth_func], GET_MANY=[auth_func],
                                            POST=[auth_func], POST_SINGLE=[auth_func], POST_MANY=[auth_func],
                                            PATCH=[auth_func], PATCH_SINGLE=[auth_func], PATCH_MANY=[auth_func],
                                            DELETE=[auth_func], DELETE_SINGLE=[auth_func], DELETE_MANY=[auth_func])
                        )

api_manager.create_api(User,
                       methods=['GET', 'POST', 'PATCH', 'DELETE'],
                       exclude_columns=['password'],
                       postprocessors=dict(GET=[get_postprocessor],
                                           GET_SINGLE=[get_postprocessor],
                                           GET_MANY=[get_postprocessor])
                       )
