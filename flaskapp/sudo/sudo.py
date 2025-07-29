from flaskapp import app
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from flaskapp.sys_lib import get_sys_info
from flaskapp.sudo.sudo_lib import sudo_check

@app.route('/sudo', methods=['GET', 'POST'])
@login_required
def sudo():
    output_text= get_sys_info()
    if not current_user.is_authenticated:
        flash ("Please Login", "warning")
        return redirect(url_for('login'))
    # os.system("echo "+password+" | sudo -S netstat -tuapn")
    # os.system('netstat -tupn > tmp')
    if request.method == 'POST':
        sudo_password_encoded = request.form['sudo_passwd']
        if not sudo_check(sudo_password_encoded):
            flash ('Wrong Sudo password!',"danger")
        else: 
            flash ('Sudo password is verified!',"success")
    return render_template('sudo/sudo.html',output_text = output_text)