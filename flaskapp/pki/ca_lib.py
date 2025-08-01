import os
from flaskapp.sys_lib import file_to_list
from flaskapp import app
from flaskapp.pki.pki_lib import get_pki_dir
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flask_login import current_user
from flask import flash

ca_csr_tmpl = app.root_path + "/pki/config/ca-csr.tmpl"
ca_csr_conf = app.root_path + "/pki/config/ca-csr.conf"
root_ca_conf = app.root_path + "/pki/config/root-ca.conf"
ca_csr = app.root_path + "/pki/config/ca.csr"
ca_key = "rsa:4096"

class X509Info:
    serial = "serial_number"
    issuer = "certificate_issuer"
    subject = "certificate_subject"
    notBefore = "begining_date"
    notAfter = "end_date"
    basicConstraints = "basicConstraints"
    keyUsage = "keyUsage"
    extendedKeyUsage = "extendedKeyUsage"

class DistinguishedName(): 
    keys = [
        "countryName", 
        "stateOrProvinceName",
        "localityName",
        "organizationName",
        "organizationalUnitName",
        "commonName",
        "emailAddress"]
    values = [
        "NR",
        "Velen",
        "Oxenfurt",
        "Tavern",
        "",
        "CommonName",
        ""
        ]

def create_ca_conf(dn=DistinguishedName()):
    # if ca template does not exist we can make default one:
    if not os.path.exists(ca_csr_tmpl):
        file = open(ca_csr_tmpl,"w")
        file.writelines(['[ req ]\n',
                         'prompt                  = no\n',
                         'distinguished_name      = ca_distinguished_name\n',
                         'req_extensions          = ca_ext\n', 
                         '\n', 
                         '[ ca_ext ]\n', 
                         'basicConstraints        = critical,CA:TRUE\n', 
                         'subjectKeyIdentifier    = hash\n', 
                         'keyUsage                = critical,keyCertSign,cRLSign\n', 
                         '\n', 
                         '[ ca_distinguished_name ]\n'])
        file.close()
    # copy template to config
    # os.system("rm " + ca_csr_conf)
    os.system("cp " + ca_csr_tmpl + " " + ca_csr_conf)
    # opening ca template for appending
    file = open (ca_csr_conf , 'a')
    x = 0
    while x < len (dn.keys):
        if dn.values[x] != '':
            file.write(dn.keys[x] + " = " + dn.values[x] + "\n")
        x = x + 1
    file.close()    

def create_ca_cert():
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
    if get_pki_dir()[0] != 'NONE':
        error = get_pki_dir()[0]
        return error
    ca_cert_dir =  get_pki_dir()[1] + "/RootCA/CA"
    # this check needs to be here
    # when user tryes to create certificate without existing PKI
    if os.system("ls " + ca_cert_dir) !=0:
        return "Can not find directory for Root CA check PKI existance."
    #1 creating  csr for CA:
    # openssl req -new -newkey rsa:4096 -keyout RootCA/CA/ca.key -config RootCA/conf/ca-request.conf -out ca.csr -nodes
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl req -new "
              + "-newkey rsa:4096 -keyout " + ca_cert_dir + "/ca.key "
              + "-config " + ca_csr_conf
              + " -out " + ca_csr + " -nodes")
    #2 making self-signed certificate
    #  openssl ca -selfsign 
    #             -in ca.csr 
    #             -config RootCA/conf/root-ca.conf 
    #             -keyfile RootCA/CA/ca.key 
    #             -out RootCA/CA/ca.cert 
    #             -batch
    #3 changing directory to keep relative directories setting in config file
    os.chdir(get_pki_dir()[1])
    os.system("echo " + current_user.sudo_password_encoded 
              + " | sudo -S openssl ca -selfsign"
              + " -in " + ca_csr
              + " -config " + root_ca_conf
              + " -keyfile " + ca_cert_dir + "/ca.key"
              + " -out " + ca_cert_dir + "/ca.cert"
              + " -batch -notext")
    return error

def get_ca_cert_info():
    error = 'NONE'
    root_ca_cert_info = X509Info()
    if get_pki_dir()[0] != 'NONE':
        error = get_pki_dir()[0]
        return error, root_ca_cert_info
    root_ca_cert_file = get_pki_dir()[1] + "/RootCA/CA/ca.cert"
    if os.system("ls " + root_ca_cert_file) !=0:
        error = "Root CA certificate is not found."
        return error, root_ca_cert_info
    root_ca_cert_info.serial = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -serial  -noout "
                                + "| sed 's/.*serial=//'").read()
    root_ca_cert_info.issuer = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -issuer  -noout "
                                + "| sed 's/.*issuer=//'").read()
    root_ca_cert_info.subject = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -subject  -noout "
                                + "| sed 's/.*subject=//'").read()    
    root_ca_cert_info.notBefore = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -startdate  -noout "
                                + "| sed 's/.*notBefore=//'").read()    
    root_ca_cert_info.notAfter = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -enddate  -noout "
                                + "| sed 's/.*notAfter=//'").read()    
    root_ca_cert_info.basicConstraints = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -ext basicConstraints  -noout "
                                + "| sed 's/.*Basic Constraints: critical'//").read()
    root_ca_cert_info.keyUsage = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -ext keyUsage  -noout "
                                + "| sed 's/.*Key Usage: critical'//").read()
    root_ca_cert_info.extendedKeyUsage = os.popen("echo " + current_user.sudo_password_encoded 
                                + " | sudo -S openssl x509 " 
                                + "-in " + root_ca_cert_file 
                                + " -ext extendedKeyUsage  -noout").read()
    return error, root_ca_cert_info

def certificate_to_list (file_path):
    cert_list = []
    temp_file = app.root_path + "/temp/temp.cert"
    os.system("echo " + current_user.sudo_password_encoded 
                        + " | sudo -S openssl x509 " 
                        + "-in " + file_path 
                        + " -text  -noout > "
                        + temp_file)
    error, cert_list = file_to_list(temp_file)
    return cert_list
    
    