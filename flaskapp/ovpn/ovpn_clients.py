from flask import render_template, flash, request
from flask_login import login_required
from flaskapp.ovpn.ovpn_clients_lib import create_ovpn_file_client, get_ovpn_clients_files
from flaskapp import app, db
from flaskapp.pki.server_client_lib import get_srvr_clnt_list

@app.route('/ovpn_clients', methods = ['POST' , 'GET'])
@login_required
def ovpn_clients():
    error, clients_list = get_srvr_clnt_list("/clients/")
    if error != 'NONE':
        clients_list = []
        flash (error, 'danger')
    error, clients_ovpn_list = get_ovpn_clients_files(clients_list)
    if error != 'NONE':
        flash (error, 'danger')
    if request.method == 'POST':
        if request.form['button_pressed'].find('recreate_') !=-1:
            file_name  = request.form['button_pressed']
            file_name = file_name[file_name.find('recreate_')+9:]
            error = create_ovpn_file_client(file_name)
            if error != 'NONE':
                flash (error, 'danger')

    return render_template('/ovpn/ovpn_clients.html' , ip_address  = '192.168.0.1:1194', clients_list = clients_list, clients_ovpn_list = clients_ovpn_list)