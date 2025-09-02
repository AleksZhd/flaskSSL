from flask import render_template, flash, request
from flask_login import login_required
from flaskapp.ovpn.ovpn_server_lib import copy_certs, get_server_status, read_server_conf
from flaskapp import app

@app.route('/ovpn_server', methods = ['GET', 'POST'])
@login_required
def ovpn_server():
    error, ovpn_status = get_server_status()
    if error != 'NONE':
        flash(error, 'danger')
    error, config_file = read_server_conf()
    if error != 'NONE':
        flash(error, 'danger')

# POST
    if  request.method == 'POST':
# install openvpn button:
        if request.form['button_pressed'] == 'copy_certs':
            error = copy_certs()

    return render_template('/ovpn/ovpn_server.html' , ovpn_status = ovpn_status , config_file = config_file)