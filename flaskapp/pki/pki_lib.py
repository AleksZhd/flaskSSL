import os
from flask import flash
from flaskapp.sys_lib import file_to_list
from flaskapp import app
from flask_login import current_user

TEMP_DIR = app.root_path + "/temp/"
PKI_DIR_FILE = app.root_path + "/pki/temp/pki_dir.txt"
SERIAL_NUMBER = "19530606AB0001"

#mkdir -p ca/root-ca/private ca/root-ca/db crl certs
def delete_pki(directory_name):
    if os.system("echo " + current_user.sudo_password_encoded + " | sudo -S rm -R "
                 + directory_name
                 +" 2>" + TEMP_DIR + "delete_pki_err") !=0:
        file = open(TEMP_DIR + "delete_pki_err")
        list = file.readlines()
        file.close()
        for message in list:
            flash (message , 'danger')
        return False
    else:
        return True

def make_dir(directory_name):
    # creating directories
    if os.system("echo " + current_user.sudo_password_encoded + " | sudo -S mkdir -p " 
                 + directory_name + "/RootCA/CA "
                 + directory_name + "/RootCA/DataBase "
                 + directory_name + "/RootCA/DataBase/certs "
                 + directory_name + "/crl "
                 + directory_name + "/server "
                 + directory_name + "/clients "
                 +" 2>" + TEMP_DIR + "dir_err") !=0:
        file = open(TEMP_DIR + "dir_err")
        list = file.readlines()
        file.close()
        for message in list:
            flash (message , 'danger')
        return False
    #creating index.txt file
    elif os.system("echo " + current_user.sudo_password_encoded + " | sudo -S touch "
                   + directory_name + "/RootCA/DataBase/index.txt "
                   +" 2>" + TEMP_DIR + "index_err") !=0:
        file = open(TEMP_DIR + "index_err")
        list = file.readlines()
        file.close()
        for message in list:
            flash (message , 'danger')
        return False
    else:
        os.system("echo " + SERIAL_NUMBER + " > " + TEMP_DIR + "serial")
        os.system("echo " + current_user.sudo_password_encoded + " | sudo -S cp "
                  + TEMP_DIR + "serial " 
                  + directory_name + "/RootCA/DataBase/")
        flash ("PKI in " + directory_name + " has been created/verified.", 'success')
        return True

def dir_tree(directory_name,including_files = False):
    error = 'NONE'
    dir_tree_list = ['Not exist.']
    if including_files:
        cmd_line = "echo " + current_user.sudo_password_encoded + " | sudo -S tree " + directory_name + " > " + TEMP_DIR + "dir_tree"
    else:
        cmd_line = "echo " + current_user.sudo_password_encoded + " | sudo -S tree -d " + directory_name + " > " + TEMP_DIR + "dir_tree"
    if os.system(cmd_line) != 0:
        #flash ("Error in 'tree' command. Mayby PKI directory is not exist yeat. Please create one.", 'warning')
        return dir_tree_list
    else:
        error, dir_tree_list = file_to_list(TEMP_DIR + "dir_tree")
        if error != 'NONE':
            flash (error, 'danger')
        return dir_tree_list

def get_pki_dir() -> tuple[ str, str ]:
    error = 'NONE'
    pki_dir = ''
    error, PKI_dir_list = file_to_list(PKI_DIR_FILE)
    if error != 'NONE':
        return error, pki_dir    
    pki_dir = PKI_dir_list[0].strip()
    if pki_dir == '':
        error = 'File is Empty: ' + PKI_DIR_FILE
    return error, pki_dir    

def update_pki_dir(directory_name):
    try:
        os.system("echo " + directory_name.strip() + " > " + PKI_DIR_FILE)
    except Exception:
        flash ( 'Error Updateing file: ' + PKI_DIR_FILE, 'danger')
        return False    
    return True
    
def read_config(file_name):
    config_list = [[]]
    error, file_list = file_to_list(file_name)
    if error != 'NONE':
        flash (error, 'danger')
    x = 0
    block = 0
    while x < len(file_list):
        if file_list[x].find('[') !=-1:
            # found a new block in cinfig file
            block = block + 1
        config_list[block][x] = file_list[x].strip()
        x = x + 1
    return config_list