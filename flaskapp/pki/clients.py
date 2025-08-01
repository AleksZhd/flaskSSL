from flask import render_template, request,redirect, url_for, flash
from flaskapp.pki.server_client_lib import get_srvr_clnt_list, create_srvr_clnt_cert
from flaskapp import app
from flask_login import login_required
from flaskapp.pki.ca_lib import DistinguishedName
from flaskapp.pki.pki_lib import get_pki_dir 
from flaskapp.pki.ca_lib import certificate_to_list 
import os


@app.route('/clients', methods = ['GET' , 'POST'])
@login_required
def clients():
    error, clients_list = get_srvr_clnt_list("/clients/")
    if error != 'NONE':
        clients_list = []
        flash (error, 'danger')
    return render_template ('/pki/clients.html',
                            clients_list = clients_list)

@app.route("/clients/<file_name>")
@login_required
def client_cert(file_name):
    certificate_file  = get_pki_dir()[1] + '/clients/' + file_name
    cert = certificate_to_list(certificate_file)
    return render_template ('/pki/server_cert.html' , cert = cert )

@app.route('/clients_create', methods = ['GET' , 'POST'])
@login_required
def clients_create():
    dn = DistinguishedName()
    dn_keys = dn.keys
    dn_values = dn.values
    if request.method == 'POST':
        x=0
        while x < len (dn_keys):
            dn_values[x] = request.form[dn_keys[x]]
            dn.values[x] = request.form[dn_keys[x]]
            x += 1
        error = create_srvr_clnt_cert(dn, True)
        if  error !=  'NONE':
            flash (error , 'danger')
        else:
            return redirect (url_for("clients")) 
    return render_template('/pki/server_create.html', 
                           dn_keys = dn_keys, 
                           dn_values = dn_values)
 
@app.route('/testing', methods = ['GET' , 'POST'])
@login_required
def testing():
    text = open('flaskapp/pki/server.conf').read()
    if request.method == 'POST':
        text = request.form['text']
        file = open('config','w')
        file.write(text)
        file.close()
    return render_template('/pki/testing.html', text = text )