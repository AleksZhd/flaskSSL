from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from flaskapp import app
from flaskapp.pki.ca_lib import DistinguishedName, certificate_to_list
from flaskapp.pki.server_lib import create_server_cert, get_server_list

@app.route("/server", methods = ['GET' , 'POST'])
@login_required
def server():
    error, server_list = get_server_list()
    if error != 'NONE':
        server_list = []
        flash (error, 'danger')
    if request.method == 'POST':
        file_name = request.form['button_pressed']
        #certificate_to_list(file_name)
    return render_template('/pki/server.html', 
                           server_list = server_list)


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
        error = create_server_cert(dn)
        if  error !=  'NONE':
            flash (error , 'danger')
        else:
            return redirect (url_for("server")) 
    return render_template('/pki/server_create.html', 
                           dn_keys = dn_keys, 
                           dn_values = dn_values)
