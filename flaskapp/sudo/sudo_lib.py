import os
from flaskapp import db, app
from flask_login import current_user
from flask import flash
from flaskapp.models.models import WebUser
from flaskapp.sys_lib import file_to_list

TEMP_DIR = app.root_path + "/temp/"

def sudo_timestemp_reset():
    if not current_user.sudo_verified:
        return False
    else:
        os.system("sudo -k") 
        os.system("echo " + current_user.sudo_password_encoded + " | sudo -S -v ")
        return True

def sudo_check(sudo_password):
#    system_user_file = TEMP_DIR + "system_user"
    user = WebUser.query.filter_by(id = current_user.id).first()
    if not user:
        flash ("Can not locate user " + current_user.web_username + " in the Database.", 'danger')
        return False
    if os.popen("id").read() == -1:
        flash ('System user' + current_user.sys_username + 'does not have sudo priveleges', "danger")
        return False
    # reset timestemp for sudo
    sudo_err_file = TEMP_DIR + "sudo.err"
    os.system("sudo -k") 
    # validating sudo password, output redirect to sudo.err file
    os.system("echo " + sudo_password + " | sudo -S -v 2>" + sudo_err_file)
    # super loop - a real programmer will cry looking at it
    output_result = file_to_list(sudo_err_file)
    if output_result[0] != 'NONE':
        flash (output_result[0], 'danger')
        return False
    else:
        x=0
        while x<len(output_result[1]):
            if output_result[1][x].find('incorrect password') !=-1:
                return False
            x=x+1
    user.sudo_password_encoded = sudo_password        
    user.sudo_verified = True
    db.session.commit()
 #   login_user(user)
    return True