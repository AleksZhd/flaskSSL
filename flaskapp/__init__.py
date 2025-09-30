from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

#SECRET_KEY is used for sessions and must be set to use flask_login and forms at least
# setting up this parameter to very small value like 'dev' is not good - flask_login did not work

app.config.from_mapping(
    SECRET_KEY='5791628bb0b13ce0c676dfde280ba245',
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flask.db'
    )

login_manager = LoginManager(app)
db = SQLAlchemy(app)
    

from flaskapp import main
from flaskapp.auth import auth
from flaskapp.network import network
from flaskapp.sudo import sudo
from flaskapp.pki import pki, ca, server, clients, revoke
from flaskapp.ovpn import ovpn_config, ovpn_server, ovpn_clients