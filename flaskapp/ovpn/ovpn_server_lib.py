import os

from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.models.models import OVPN_INFO
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flask_login import current_user
from flaskapp import app
from flask import flash

TEMP_DIR = app.root_path + "/temp/"

# nor working
def copy_certs():
    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    # call read_server_conf to copy server file to temp directory
    # and make config_string
    error, config_string = read_server_conf()
    if config_string == "_empty_":
        error = "Error copying or reading server configuration file"
        return error
    # getting PKI directory
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        return error
    # setting ca certificate value
    ca_cert = pki_dir + '/RootCA/CA/ca.cert'
    error, config_string = change_setting_value(config_string, 'ca', ca_cert)
    if error != 'NONE':
        return error
    # setting server certificate and key
    server_files = os.popen("ls " + pki_dir + "/server/ | grep cert").read()
    if server_files == '':
        return "Could not find server certificate"
    else:
        # here we take first certificate in server folders
        server_file_name = server_files.split()[0].split('.')[0]
        server_cert = server_file_name + '.cert'
        server_key = server_file_name + '.key'
        error, config_string = change_setting_value(config_string, 'cert', pki_dir + '/server/' + server_cert)
        if error != 'NONE':
            return error
        error, config_string = change_setting_value(config_string, 'key', pki_dir + '/server/' +  server_key)
        if error != 'NONE':
            return error
    error = save_server_conf(config_string)
#    file = open(TEMP_DIR + "server.tmp","w")
#    file.write(config_string)
#    file.close()
    return error

def change_setting_value(config_string, the_setting, the_value=''):
    error = 'NONE'
    if config_string == '' or the_setting == '':
        return 'Empty config string or setting.', config_string
    # config_string is basically file with settings
    # function looks and find 'the_settings' in the begining of strings
    # if it finds "the_value" will be new
    # 1 making list by splitting string at '\n' 
    config_list = config_string.split('\n')
    # 2 finding setting and meking new value
    found = False
    index=0
    for element in config_list:
        if element.find(the_setting) == 0:
            config_list[index] = the_setting + ' ' + the_value
            found = True
        index += 1
    if not found:
        error = 'Coud not find setting: ' + the_setting
    # remaking string from the list
    config_string = '\n'.join(config_list)
    return error, config_string
# end of not working

def get_server_logs():
    log  = os.popen("echo " + current_user.sudo_password_encoded
                    + " | sudo -S cat /var/log/openvpn/openvpn.log").read()
    status  = os.popen("echo " + current_user.sudo_password_encoded
                    + " | sudo -S cat /var/log/openvpn/openvpn-status.log").read()

    return log, status

def change_server_status(status='restart',id=1):
    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    file_path = OVPN.server_file
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S systemctl " + status + " openvpn@" 
              + os.path.splitext(file_path)[0])
    return error

def save_server_conf(config_string='', id=1):
    error  = "NONE"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    # saving string into template file:
    new_file = open(TEMP_DIR + 'server.new', 'w')
    new_file.write(config_string)
    new_file.close()
    # copy new config file to openVPN directory
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    file_path = OVPN.main_dir + OVPN.server_file
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S cp " 
              + TEMP_DIR + 'server.new '
              + file_path)
    return error

def read_server_conf(id=1):
    error  = "NONE"
    config_file = "_empty_"
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error, config_file
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    from_path = OVPN.main_dir + OVPN.server_file
    to_path = TEMP_DIR + OVPN.server_file
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
    server_name = os.path.splitext(server_file)[0]
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S systemctl status openvpn@" 
              + server_name 
              + " > " + TEMP_DIR + "ovpn_server.status")
    os.system("echo '#---- netstat ----#' >> "+ TEMP_DIR + "ovpn_server.status")
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S netstat -tuapn | grep openvpn"
              + " >> " + TEMP_DIR + "ovpn_server.status")    
    server_status = open(TEMP_DIR + "ovpn_server.status").read()
    return error, server_status