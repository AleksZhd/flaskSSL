import os
from flaskapp import app
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flask import flash
TEMP_DIR = app.root_path + "/temp/"


def get_network_info():
    list = []
    if not sudo_timestemp_reset():
        flash ("sudo password is not set/valid", "danger")
        return list
    else:
        os.system("date >" + TEMP_DIR + "network_info")
        os.system("netstat -rn >>" + TEMP_DIR + "network_info")
        os.system("netplan status >>" + TEMP_DIR + "network_info")
        os.system("resolvectl >>" + TEMP_DIR + "network_info")
        
        file = open(TEMP_DIR + "network_info")
        list = file.readlines()
        file.close()
    return list

def get_netstat_info():
    list = []
    if not sudo_timestemp_reset():
        flash ("sudo password is not set/valid", "danger")
        return list
    else:
        os.system("date >" + TEMP_DIR + "netstat_info")
        os.system("sudo netstat -tupan >>" + TEMP_DIR + "netstat_info")
        file = open(TEMP_DIR + "netstat_info")
        list = file.readlines()
        file.close()
    return list