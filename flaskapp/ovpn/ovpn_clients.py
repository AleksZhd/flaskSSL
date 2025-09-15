from flask import redirect, render_template, flash, request, url_for, send_file
from flask_login import login_required
from flaskapp.ovpn.ovpn_clients_lib import create_ovpn_file_client, get_ovpn_clients_files, get_protocol
from flaskapp import app, db
from flaskapp.pki.server_client_lib import get_srvr_clnt_list
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
import os
from flaskapp.models.models import OVPN_INFO
from flask_login import current_user

@app.route('/ovpn_clients', methods = ['POST' , 'GET'])
@login_required
def ovpn_clients():
    # reading clients certificates list from PKI:
    error, clients_list = get_srvr_clnt_list("/clients/")
    if error != 'NONE':
        clients_list = []
        flash (error, 'danger')
    # reading ovpn clients files from Open VPN directory:
    error, clients_ovpn_list = get_ovpn_clients_files(clients_list)
    if error != 'NONE':
        flash (error, 'danger')
    # reading ip address from the file:
    ip_address = open(app.root_path + "/ovpn/templates/ip_address").read()
    # reading from server configuration file what protocol is in use:
    error, tcp_protocol = get_protocol()
    if error != 'NONE':
        flash (error, 'danger')
    # POST section:
    if request.method == 'POST':
        if request.form['button_pressed'].find('recreate_') !=-1:
            # rewriting ip address file
            ip_address = request.form['ip_address']
            file = open (app.root_path + "/ovpn/templates/ip_address" , "w")
            file.write(ip_address)
            file.close()
            # reading file name
            file_name  = request.form['button_pressed']
            file_name = file_name[file_name.find('recreate_')+9:]
            # reading protocol from radio button:
            protocol = request.form['radio_button']
            error = create_ovpn_file_client(file_name, protocol)
            if error != 'NONE':
                flash (error, 'danger')
            return redirect(url_for ('ovpn_clients'))
        if request.form['button_pressed'].find('edit_') !=-1:
            if request.form['button_pressed'] == "edit_File is not found":
                flash ("Create .ovpn file first.", 'warning')
                return redirect(url_for ('ovpn_clients'))
            file_name  = request.form['button_pressed']
            file_name = file_name[file_name.find('edit_')+5:]
            return redirect(url_for('edit_ovpn_client', file_name = file_name))
        if request.form['button_pressed'].find('download_') !=-1:
            if request.form['button_pressed'] == "download_File is not found":
                flash ("Create .ovpn file first.", 'warning')
                return redirect(url_for ('ovpn_clients'))
            file_name  = request.form['button_pressed']
            file_name = file_name[file_name.find('download_')+9:]
            OVPN = OVPN_INFO.query.filter_by(id = 1).first()
            file_path = OVPN.main_dir + "clients_ovpn/" + file_name
            return send_file(file_path, as_attachment=True)
            

    return render_template('/ovpn/ovpn_clients.html' , 
                           ip_address  = ip_address, 
                           clients_list = clients_list, 
                           clients_ovpn_list = clients_ovpn_list,
                           tcp_protocol = tcp_protocol)

@app.route("/ovpn_client/<file_name>", methods = ['GET' , 'POST'])
@login_required
def edit_ovpn_client(file_name):
    if not sudo_timestemp_reset():
        flash('Please check/reset SUDO password', 'danger')
        return redirect(url_for ('ovpn_clients'))
    OVPN = OVPN_INFO.query.filter_by(id = 1).first()
    file_path = OVPN.main_dir + "clients_ovpn/" + file_name
    file_string = os.popen("echo " + current_user.sudo_password_encoded + " | sudo -S cat " + file_path).read().strip()
    if request.method == 'POST':
        if request.form['button_pressed'] == 'back':
            return redirect(url_for ('ovpn_clients'))
        if request.form['button_pressed'] == 'save':
            #saving string to temp file:
            temp_file_path = app.root_path + "/ovpn/templates/temp.ovpn"
            temp_file = open(temp_file_path, 'w')
            temp_file.write(request.form['file_string'])
            temp_file.close()
            os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S mv " + temp_file_path
              + " " 
              + OVPN.main_dir + "clients_ovpn/" + file_name)
            return redirect(url_for ('ovpn_clients'))
    return render_template('/ovpn/edit_ovpn_client.html', file_name = file_name, file_string = file_string)