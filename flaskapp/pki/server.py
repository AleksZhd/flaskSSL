from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp import app
from flaskapp.pki.ca_lib import DistinguishedName, certificate_to_list
from flaskapp.pki.server_client_lib import create_srvr_clnt_cert, get_srvr_clnt_list

@app.route("/server", methods = ['GET' , 'POST'])
@login_required
def server():
    error, server_list = get_srvr_clnt_list()
    if error != 'NONE':
        server_list = []
        flash (error, 'danger')
    file_list = len (server_list) * ['']
    file_dir = get_pki_dir()[1] + '/server/'
    x=0
    while x < len (server_list):
        file_list[x] = file_dir + server_list[x]
        x += 1
    return render_template('/pki/server.html', 
                           server_list = server_list,
                           file_list = file_list)

@app.route("/server/<file_name>")
@login_required
def server_cert(file_name):
    certificate_file  = get_pki_dir()[1] + '/server/' + file_name
    cert = certificate_to_list(certificate_file)
    return render_template ('/pki/server_cert.html' , cert = cert )

@app.route("/server_create", methods = ['GET' , 'POST'])
@login_required
def server_create():
    dn = DistinguishedName()
    dn_keys = dn.keys
    dn_values = dn.values
    if request.method == 'POST':
        x=0
        while x < len (dn_keys):
            dn_values[x] = request.form[dn_keys[x]]
            dn.values[x] = request.form[dn_keys[x]]
            x += 1
        error = create_srvr_clnt_cert(dn)
        if  error !=  'NONE':
            flash (error , 'danger')
        else:
            return redirect (url_for("server")) 
    return render_template('/pki/server_create.html', 
                           dn_keys = dn_keys, 
                           dn_values = dn_values,
                           server=True)
