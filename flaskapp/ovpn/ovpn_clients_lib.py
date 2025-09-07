from http import client
from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset 
from flaskapp.pki.server_client_lib import get_srvr_clnt_list
from flaskapp import app, db
import os
from flask_login import current_user
from flaskapp.models.models import OVPN_INFO

CLIENT_TMPL_FILE =  app.root_path + "/ovpn/templates/client.tmpl"
TMPL_DIR = app.root_path + "/ovpn/templates/"

def get_ovpn_clients_files(clients_cert_list=[]):
    # function recives clients certificates list and tryes to find ovpn configuration files
    clients_ovpn_list = [] * len(clients_cert_list)

    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error , clients_ovpn_list
    OVPN = OVPN_INFO.query.filter_by(id = 1).first()
    clients_ovpn_list = [''] * len(clients_cert_list)
    x=0
    for client_cert in clients_cert_list:
        client_ovpn_file = client_cert.split('.')[0]+'.ovpn'
        if os.system("ls " + OVPN.main_dir + "clients_ovpn/" + client_ovpn_file) == 0:
            clients_ovpn_list[x] = client_ovpn_file
        else:
            clients_ovpn_list[x] = "File is not found"
        x += 1
    return error , clients_ovpn_list

def create_ovpn_file_client(client_cert=''):
    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    # lets check if client certificate exist:
    error, clients_list = get_srvr_clnt_list("/clients/")
    if error != 'NONE':
        return error
    existence = False
    for client in clients_list:
        if client == client_cert:
            existence = True
    if not existence:
        error = 'Could not find client`s certificate: ' + client_cert
        return error
    # lets do ovpn file:
    # changing file extension:
    client_ovpn = client_cert.split('.')[0]+'.ovpn'
    # reading client template file as string
    client_tmpl = open(CLIENT_TMPL_FILE).read()
    # inserting certificates:
    # CA certificate:
    ca_file =  get_pki_dir()[1] + "/RootCA/CA/ca.cert"
    ca_cert = os.popen("echo " + current_user.sudo_password_encoded + " | sudo -S cat " + ca_file).read().strip()
    client_tmpl = client_tmpl[:client_tmpl.find('\n<ca>\n')+6] + ca_cert + client_tmpl[client_tmpl.find('\n</ca>\n'):]
    # client`s certificate`
    client_file_cert =  get_pki_dir()[1] + "/clients/" + client_cert
    client_certificate = os.popen("echo " + current_user.sudo_password_encoded + " | sudo -S cat " + client_file_cert).read().strip()
    client_tmpl = client_tmpl[:client_tmpl.find('\n<cert>\n')+8] + client_certificate + client_tmpl[client_tmpl.find('\n</cert>\n'):]
    # client`s key
    client_file_key = get_pki_dir()[1] + "/clients/" + client_cert.split('.')[0]+'.key'
    client_key = os.popen("echo " + current_user.sudo_password_encoded + " | sudo -S cat " + client_file_key).read().strip()
    client_tmpl = client_tmpl[:client_tmpl.find('\n<key>\n')+7] + client_key + client_tmpl[client_tmpl.find('\n</key>\n'):]
    # TA key
    OVPN = OVPN_INFO.query.filter_by(id = 1).first()
    ta_file = OVPN.main_dir + "ta.key"
    ta_key = os.popen("echo " + current_user.sudo_password_encoded + " | sudo -S cat " + ta_file).read().strip()
    client_tmpl = client_tmpl[:client_tmpl.find('\n<tls-auth>\n')+12] + ta_key + client_tmpl[client_tmpl.find('\n</tls-auth>\n'):]
    #
    file = open(TMPL_DIR+client_ovpn,'w')
    file.write(client_tmpl)
    file.close
    # moving file to openvpn directory
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S mv " + TMPL_DIR + client_ovpn
              + " " 
              + OVPN.main_dir + "clients_ovpn")
    return error