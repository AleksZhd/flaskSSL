import os
from flaskapp import app, db
from flask import flash

TEMP_DIR = app.root_path + "/temp/"

def file_to_list(file_name: str) -> list:
    error = 'NONE'
    output_list = ['']
    # open works according linux permissions and sudo is not applied in this case,
    # the file must be availble for reading for the linux user
    try:
        file = open(file_name)
    except FileNotFoundError:
        error = "File "+ file_name + " was not found"    
    except PermissionError:
        error = "Permission Error at opening file: " + file_name
    except:
        error = "Unexpected error at opening file: "+ file_name
    else:
        output_list = file.readlines()
        file.close()
        if len(output_list) == 0:
            error = "File " + file_name + " is empty."
        else:
            # if file opens and is not empty lets get rid of "enters" but not strip
            x=0
            while x<len(output_list):
                output_list[x] = output_list[x][:output_list[x].find('\n')]
                x=x+1
    return [error, output_list]

def get_sys_info():
    os.system("echo System: >" + TEMP_DIR + "system_info")
    os.system("uname -snmr >>" + TEMP_DIR + "system_info")
    os.system("echo ----- >>" + TEMP_DIR + "system_info")
    os.system("echo Uptime: >>" + TEMP_DIR + "system_info")
    os.system("uptime >>" + TEMP_DIR + "system_info")
    os.system("echo ----- >>" + TEMP_DIR + "system_info")
#    os.system("echo netplan: >>" + TEMP_DIR + "system_info")
#    os.system("netplan status >>" + TEMP_DIR + "system_info")
#    os.system("echo ----- >>" + TEMP_DIR + "system_info")
#    os.system("echo Disks: >>" + TEMP_DIR + "system_info")
#    os.system("df -hT >>" + TEMP_DIR + "system_info")
#    os.system("echo ----- >>" + TEMP_DIR + "system_info")
    os.system("echo Memory: >>" + TEMP_DIR + "system_info")
    os.system("free -h >>" + TEMP_DIR + "system_info")      
    os.system("echo ----- >>" + TEMP_DIR + "system_info")
    os.system("date >>" + TEMP_DIR + "system_info")
    file = open(TEMP_DIR + "system_info")
    list = file.readlines()
    file.close()
    return list


