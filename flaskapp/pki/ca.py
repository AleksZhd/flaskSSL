from flask import redirect, render_template, request, url_for
from flask_login import login_required
from flaskapp import app
from flaskapp.pki.pki_lib import get_pki_dir
import os
from flask import flash
from flaskapp.sys_lib import file_to_list
from flaskapp.pki.ca_lib import DistinguishedName, X509Info, create_ca_conf,create_ca_cert, get_ca_cert_info, certificate_to_list

@app.route('/ca', methods = ['POST' , 'GET'])
@login_required
def ca():
    certificate = []
    root_ca_info = X509Info()
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        flash (error, 'danger')
        return ('System Error')
    ca_cert_file = pki_dir + "/RootCA/CA/ca.cert"
    if os.system("ls " + ca_cert_file) !=0:
        flash ("File " + ca_cert_file + " does NOT exist!", 'warning')
    else:
        error, root_ca_info = get_ca_cert_info()
        certificate = certificate_to_list (ca_cert_file)
    return render_template('/pki/ca.html', ca_cert_file = ca_cert_file, ca_info = root_ca_info, certificate = certificate)

@app.route('/ca_create', methods = ['POST' , 'GET'])
@login_required
def ca_create():
    dn = DistinguishedName()
    dn_keys = dn.keys
    dn_values = dn.values
    if request.method == 'POST':
        x=0
        while x < len (dn_keys):
            dn_values[x] = request.form[dn_keys[x]]
            dn.values[x] = request.form[dn_keys[x]]
            x += 1
        create_ca_conf(dn)
        error = create_ca_cert()
        if  error !=  'NONE':
            flash (error , 'danger')
        else:
            return redirect (url_for("ca")) 
    return render_template('/pki/ca_create.html' ,dn_keys = dn_keys , dn_values = dn_values)