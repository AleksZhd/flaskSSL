from http import client
import ipaddress
from flaskapp.ovpn.ovpn_server_lib import read_server_conf
from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset 
from flaskapp.pki.server_client_lib import get_srvr_clnt_list
from flaskapp import app, db
import os
from flask_login import current_user
from flaskapp.models.models import OVPN_INFO

CLIENT_TMPL_FILE =  app.root_path + "/ovpn/templates/client.tmpl"
TMPL_DIR = app.root_path + "/ovpn/templates/"

def get_protocol():
    error = 'NONE'
    tcp_protocol = False
    # reading server config into the string
    error, server_config = read_server_conf(id=1)
    if error != 'NONE':
        return error, tcp_protocol
    # finfing uncommented "proto" string:
    begining_protocol = server_config[server_config.find("\nproto")+1:]
    protocol = begining_protocol[:begining_protocol.find("\n")]
    # checking if the string has tcp inside:
    if protocol.find("tcp") !=-1:
        tcp_protocol = True
    return error, tcp_protocol

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

def create_ovpn_file_client(client_cert='',protocol='udp'):
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
    # changing ip address and port number:
    ip_address = client_tmpl[client_tmpl.find("\nremote")+1:] #from "\nremote" to the end of the file without first "\n"
    ip_address = ip_address[:ip_address.find("\n")] #now cutting evrething from the next "\n" to the end of the file
    # new ip addrees from the file by splitting at ":" , we got a list. index 0 - ip, index 1 - port number
    new_ip_address_list = open(app.root_path + "/ovpn/templates/ip_address").read().split(':')
    # making new ip address and port number string
    new_ip_address = "remote " + new_ip_address_list[0] + " " + new_ip_address_list[1]
    # replacing ip address:
    client_tmpl = client_tmpl.replace(ip_address, new_ip_address)
    # changing protocol:
    proto_string = client_tmpl[client_tmpl.find("\nproto")+1:] # from "\nproto" to the end of the file without first "\n"
    proto_string = proto_string[:proto_string.find("\n")] # now cutting evrething from the next "\n" to the end of the file
    new_proto_string = "proto " + protocol
    # replacing protocol:
    client_tmpl = client_tmpl.replace(proto_string, new_proto_string)
    # saving into the file
    file = open(TMPL_DIR+client_ovpn,'w')
    file.write(client_tmpl)
    file.close
    # moving file to openvpn directory
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S mv " + TMPL_DIR + client_ovpn
              + " " 
              + OVPN.main_dir + "clients_ovpn")
    return error