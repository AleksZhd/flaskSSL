import os
from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flask_login import current_user, login_required
from flaskapp import app, db
from flask import redirect, render_template, flash, request, url_for
from flaskapp.pki.server_client_lib import get_srvr_clnt_list

@app.route('/revoke' , methods =['GET', 'POST'])
@login_required
def revoke():
    error, index_list = read_index_txt()
    if error != 'NONE':
        flash (error, 'danger')
    error, revokation_status_list = check_revocations(index_list)
    if error != 'NONE':
        revokation_status_list = [['err','err','err']]
        flash (error, 'danger')
    if request.method == 'POST':
        client_cert = request.form['button_pressed']
        return redirect(url_for('revoke_cert', client_cert = client_cert))
    return render_template('pki/revoke.html', 
                           index_list = index_list,
                            revokation_status_list = revokation_status_list )

@app.route("/revoke_cert/<client_cert>", methods = ['GET' , 'POST'])
@login_required
def revoke_cert(client_cert):
# GET section
    # checking sudo for later use
    if not sudo_timestemp_reset():
        flash('Please check/reset SUDO password', 'danger')
        return redirect(url_for('revoke'))
    # getting PKI directory
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        flash(error, 'danger')
        return redirect(url_for('revoke'))
    # file path for client certificate
    file_path = pki_dir + '/clients/' + client_cert
    # getting subject(destinguished name) from the certificate
    #sudo openssl x509 -in /etc/test/clients/aleksandr.cert -subject -noout
    subject = os.popen("echo " + current_user.sudo_password_encoded + " | sudo openssl x509 -in " + file_path +" -subject -noout").read().strip()
    # hetting rid of extra words:
    d_name = subject.replace('subject=','')

# POST section
    if request.method == 'POST':
        # presed cancel - redirect to revoke page
        if request.form['button_pressed'] == 'Cancel':
            return redirect(url_for('revoke'))
        # pressed Revoke:
        if request.form['button_pressed'] == 'Revoke':
            reason = request.form['radio_button']
            error = revoke_client_cert(client_cert, reason)
            return redirect(url_for('revoke'))
    return render_template('pki/revoke_client_cert.html', client_cert=client_cert, d_name = d_name)

def revoke_client_cert(client_cert, reason ):
    error = 'NONE'
    if not sudo_timestemp_reset():
        return 'Check sudo password'
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        return error
    client_cert_file = pki_dir + '/clients/' + client_cert
    # root CA configuration file directory:
    root_ca_conf = app.root_path + "/pki/config/root-ca.conf"
    # changing working dir:
    os.chdir(pki_dir)
    # revocation command:
    #  sudo openssl ca -config /home/aleks/flaskSSL/flaskapp/pki/config/root-ca.conf -revoke /etc/test/clients/gleb.cert -crl_reason keyCompromise
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl ca "
              + "-config " + root_ca_conf
              + " -revoke " + client_cert_file 
              + " -crl_reason " + reason)
    # updating crl.pem
    # sudo openssl ca -config /home/aleks/flaskSSL/flaskapp/pki/config/root-ca.conf -extensions crl_ext -gencrl -out crl/crl.pem
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl ca "
              + "-config " + root_ca_conf
              + " -extensions crl_ext -gencrl"
              + " -out crl/crl.pem")
    return error

  # ReasonFlags ::= BIT STRING {
#        unused                  (0),
#        keyCompromise           (1),
#        cACompromise            (2),
#        affiliationChanged      (3),
#        superseded              (4),
#        cessationOfOperation    (5),
#        certificateHold         (6) }



def check_revocations(index_list=[['']]):
    # input as lists inside list for index.txt
    error = 'NONE'
    revocation_status_list = [['','','']] # 'cert name', 'R/V', 'date of revocation'
    # gathering all clients .cert files
    error, clients_list = get_srvr_clnt_list("/clients/")
    if error != 'NONE':
        return error, revocation_status_list
    # getting directory
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        return error, revocation_status_list
    CLIENTS_DIR = pki_dir + "/clients/"
    # how to find serial number of clinet`s certificate:`
    #  os.popen('openssl x509 -in /etc/test/clients/aleksandr.cert -serial -noout').read().strip().split('=')[1]
    serial_list = [''] * len(clients_list)
    x = 0 
    while x < len(clients_list):
        serial_list[x] = os.popen('openssl x509 -in '
                            + CLIENTS_DIR + clients_list[x] 
                            + ' -serial -noout').read().strip().split('=')[1]
        x = x + 1
    # now we have serial_list and clients_list equivalent 
    # going trought serial_list and looking at status in index.txt
    revocation_status_list = [['','','']] * len(serial_list)
    x = 0
    while x < len(serial_list):
        y = 0
        while y < len(index_list):
            if serial_list[x] == index_list[y][3]:
                revocation_status_list[x]  = [ clients_list[x],index_list[y][0],index_list[y][2]]
            y = y + 1
        x = x + 1
    return error, revocation_status_list

def read_index_txt():
    error = 'NONE'
    temp_list =['']
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error, temp_list 
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        return error, temp_list
    # copying index.txt to temp directory, using 'cat' to avoid permission problems (instead of copying and changing owner) 
    os.system("cat " + pki_dir + "/RootCA/DataBase/index.txt > "
              + app.root_path + "/temp/index.txt" )
    # making list with entire line as element:
    file_list = open(app.root_path + "/temp/index.txt").read().split('\n')
    # index_list is lists inside the list for table representation of the index.txt
    index_list = [['']] * len(file_list)
    x = 0
    while x < len(file_list):
        if file_list[x] != '':
            index_list[x] = file_list[x].split('\t')
        else:
            index_list.pop(x)
        x = x + 1
    return error, index_list