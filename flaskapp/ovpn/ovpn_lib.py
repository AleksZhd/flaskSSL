import os
from flaskapp import db, app
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flaskapp.models.models import OVPN_INFO
from flask_login import current_user
from flaskapp.pki.pki_lib import file_to_list

TEMP_DIR = app.root_path + "/temp/"
SERVER_CONF_PATH = app.root_path + "/ovpn/templates/server.conf"

def create_files(id=1):
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    OVPN = OVPN_INFO.query.filter_by(id=id).first()
    os.chdir(OVPN.main_dir)
# cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/server.conf
#   os.system("echo " + current_user.sudo_password_encoded + " | sudo -S cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/server.conf")
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S cp " + SERVER_CONF_PATH + " /etc/openvpn/server.conf")
# cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf /etc/openvpn/client.conf
#    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf /etc/openvpn/client.conf")
# openvpn --genkey secret ta.key
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S openvpn --genkey secret ta.key")
# openssl dhparam -out dh2048.pem 2048
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S openssl dhparam -out dh2048.pem 2048")
# making directory for clients ovpn configuration files
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S mkdir " + OVPN.main_dir + "clients_ovpn")
    return error



def install_ovpn():
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    #root directory
    os.chdir('/')
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S apt update")
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S apt remove openvpn -y")
    os.system("echo " + current_user.sudo_password_encoded + " | sudo -S apt install openvpn -y")
    return error  

def get_ovpn_config(id=1):
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
# init table in DataBase if no records found    
    OVPN = OVPN_INFO.query.filter_by(id = id).first()
    if not OVPN:
        OVPN = OVPN_INFO()
        OVPN.name = 'Default OVPN'
        db.session.add(OVPN)
        db.session.commit()
        get_ovpn_config(id=id)
# directoty
    if os.system("ls " + OVPN.main_dir) ==0:
        OVPN.main_dir_set = True
    else:
        OVPN.main_dir_set = False
# server file
    if os.system("ls " + OVPN.main_dir + OVPN.server_file) == 0 and OVPN.server_file !='':
        OVPN.server_file_set = True
    else: 
        OVPN.server_file_set = False
# client file
    if os.system("ls " + OVPN.main_dir + OVPN.client_file) == 0 and OVPN.client_file !='':
        OVPN.client_file_set = True
    else:
        OVPN.client_file_set = False
# dh file
    if os.system("ls " + OVPN.main_dir + OVPN.dh_file) == 0 and OVPN.dh_file != '':
        OVPN.dh_file_set = True
    else:
        OVPN.dh_file_set = False
# TA file
    if os.system("ls " + OVPN.main_dir + OVPN.ta_file) == 0 and OVPN.ta_file != '':
        OVPN.ta_file_set = True
    else:
        OVPN.ta_file_set = False
    db.session.commit()
    return error

def get_ovpn_tree(id=1):
    error = 'NONE'
    ovpn_tree_list = 'Not exist.'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error, ovpn_tree_list
    OVPN = OVPN_INFO.query.filter_by(id = id).first()
    if not OVPN:
        error = 'OVPN Database record is not found.'
        return error, ovpn_tree_list
    directory_name = OVPN.main_dir
    cmd_line = "echo " + current_user.sudo_password_encoded + " | sudo -S ls -w 1 -p " + directory_name + " > " + TEMP_DIR + "ovpn_tree"
    if os.system(cmd_line) != 0:
        #flash ("Error in 'tree' command. Mayby PKI directory is not exist yeat. Please create one.", 'warning')
        return error, ovpn_tree_list
    else:
        # reading as one line NOT LIST
        ovpn_tree_list = open(TEMP_DIR + "ovpn_tree").read()
        return error, ovpn_tree_list
