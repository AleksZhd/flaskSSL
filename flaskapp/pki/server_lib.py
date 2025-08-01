from flaskapp.pki.ca_lib import DistinguishedName
import os
from flaskapp import app
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flaskapp.pki.pki_lib import get_pki_dir
from flask_login import current_user
from flask import flash

server_csr_tmpl = app.root_path + "/pki/temp/server-csr.tmpl"
server_csr_conf = app.root_path + "/pki/temp/server-csr.conf"
root_ca_conf = app.root_path + "/pki/temp/root-ca.conf"
server_csr = app.root_path + "/pki/temp/server.csr"

def get_server_list(path = "/server/"):
    error = 'NONE'
    server_list = []
    server_cert_dir =  get_pki_dir()[1] + path    
    if os.system("ls " + server_cert_dir) !=0:
        error = "Can not find directory " + server_cert_dir +" check PKI existance."
        return error, server_list
    server_list = os.popen('ls ' + server_cert_dir + ' | grep .cert').read().split()
    return error, server_list

def create_server_cert(dn=DistinguishedName(), client = False):
#1 prelimenary checks:
    if client:
        flash ("CLIENT")
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    if get_pki_dir()[0] != 'NONE':
        error = get_pki_dir()[0]
        return error
    server_cert_dir =  get_pki_dir()[1] + "/server"
    clients_cert_dir =  get_pki_dir()[1] + "/clients"
    # this check needs to be here
    # when user tryes to create certufucate without existing PKI
    if os.system("ls " + server_cert_dir) !=0:
        return "Can not find directory for Server check PKI existance."
    if client and os.system("ls " + server_cert_dir) !=0:
        return "Can not find directory for Clients check PKI existance."
    if dn.values[5] == '':
        error = 'Common Name can not be empty'
        return error
    else:
        file_name = "_".join(dn.values[5].lower().split())
#2 creating config
    if not os.path.exists(server_csr_tmpl):
        file = open(server_csr_tmpl,"w")
        file.writelines(['[ req ]\n',
                         'prompt                  = no\n',
                         'distinguished_name      = server_dn\n',
                         '\n', 
                         '[ server_dn ]\n'])
        file.close()
    os.system("cp " + server_csr_tmpl + " " + server_csr_conf)
    # opening ca template for appending
    file = open (server_csr_conf , 'a')
    x = 0
    while x < len (dn.keys):
        if dn.values[x] != '':
            file.write(dn.keys[x] + " = " + dn.values[x] + "\n")
        x = x + 1
    file.close()
    if client:
        certificate_dir = clients_cert_dir
        extension = "client_extensions"
    else:
        certificate_dir = server_cert_dir
        extension = "server_extensions"
#3 creating  csr for server:
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl req -new "
              + "-newkey rsa:2048 -keyout " + certificate_dir + "/" + file_name + ".key "
              + "-config " + server_csr_conf
              + " -out " + server_csr + " -nodes")
#4 creating certificate for server
    os.chdir(get_pki_dir()[1])
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl ca"
              + " -in " + server_csr
              + " -config " + root_ca_conf
              + " -extensions " + extension
              + " -out " + certificate_dir + "/" + file_name + ".cert"
              + " -batch -notext")
    return error