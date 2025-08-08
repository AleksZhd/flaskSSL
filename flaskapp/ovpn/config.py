from flask import render_template
from flask_login import login_required
from flaskapp import app
from flaskapp.ovpn.ovpn_lib import get_ovpn_config

@app.route('/ovpn_config', methods  = ['POST' , 'GET'])
@login_required
def ovpn_config():
    get_ovpn_config()
    return render_template ('/ovpn/config.html')