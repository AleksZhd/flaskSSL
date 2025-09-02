import os

from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.models.models import OVPN_INFO
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flask_login import current_user
from flaskapp import app

TEMP_DIR = app.root_path + "/temp/"

def copy_certs():
    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    # call read_server_conf to copy server file to temp directory
    # and make config_string
    error, config_string = read_server_conf()
    if config_string == "_empty_":
        error = "Error coping or reading server configuration file"
        return error
    #1 changing ca line
    # looking betweeng "ca" and "cert" - it will work only with sefault config file
    # result will be something - '\nca ca.crt'
    cert = config_string[config_string.find("\nca"):config_string.find("\ncert")]
    # looking on current ca certificate in PKI
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        return error
    new_cert = "\nca " + pki_dir + "/RootCA/CA/ca.cert"
    # replaceing certificates
    config_string = config_string.replace(cert,new_cert)
    #new file 
    file = open(TEMP_DIR + "server.tmp","w")
    file.write(config_string)
    file.close()
    return error

def read_server_conf(id=1):
    error  = "NONE"
    config_file = "_empty_"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error, config_file
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    from_path = OVPN.main_dir + OVPN.server_file
    to_path = TEMP_DIR + OVPN.server_file[1:]
    #1 copy server config file to temp directory
    # with will help to open this file to write without sudo permission
    # and cope command will be without sudo to rewrite permissions on the file
    # cp /etc/openvpn/server.conf ~/flaskSSL/server.conf
    os.system("cp " + from_path + " " + to_path)
    config_file = open(to_path).read()
    return error, config_file


def get_server_status(id=1):
    error = 'NONE'
    server_status = ""
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error, server_status
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    server_file = OVPN.server_file
    # as example lets server_file = '/server.conf'
    # os.path.splitext(server_file) returns list :('/server', '.conf')
    # we take it first item which is [0] - it is string now
    # and cut this string from second letter  to last letter in it by [1:] - count starts from 0
    server_name = os.path.splitext(server_file)[0][1:]
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S systemctl status openvpn@" 
              + server_name 
              + " > " + TEMP_DIR + "ovpn_server.status")
    server_status = open(TEMP_DIR + "ovpn_server.status").read()
    return error, server_status