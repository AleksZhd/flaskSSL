
from flask import redirect, render_template, flash, request, url_for
from flask_login import login_required
from flaskapp.models.ovpn_models import Server_settings
from flaskapp.ovpn.ovpn_server_lib import change_server_status, copy_certs, get_server_logs, get_server_status, read_server_conf, save_server_conf
from flaskapp import app, db

@app.route('/ovpn_server', methods = ['GET', 'POST'])
@login_required
def ovpn_server():
    error, ovpn_status = get_server_status()
    if error != 'NONE':
        flash(error, 'danger')
    error, config_file = read_server_conf()
    if error != 'NONE':
        flash(error, 'danger')

# POST
    if  request.method == 'POST':
# saving config:
        if request.form['button_pressed'] == 'save_config':
            error = save_server_conf(request.form['conf_string'],1)
            if error != 'NONE':
                flash(error, 'danger')
            return redirect (url_for('ovpn_server'))
        if (request.form['button_pressed'] == 'start') or (request.form['button_pressed'] == 'stop') or (request.form['button_pressed'] == 'restart') or (request.form['button_pressed'] == 'enable'):
            error = change_server_status(request.form['button_pressed'])
            return redirect (url_for('ovpn_server'))
        if request.form['button_pressed'] == 'copy_certs':
            error = copy_certs()
            if error != 'NONE':
                flash (error, 'danger')
            return redirect(url_for('ovpn_server'))
    return render_template('/ovpn/ovpn_server.html' , ovpn_status = ovpn_status , config_file = config_file)


@app.route('/ovpn_server_logs', methods = ['GET', 'POST'])
@login_required
def ovpn_server_logs():
    log, status = get_server_logs()

    return render_template('/ovpn/ovpn_server_logs.html' , log = log , status = status)

# left this idea to other time
# do not use it now
@app.route('/ovpn_server/setup', methods = ['GET', 'POST'])
@login_required
def ovpn_server_setup():
    all_settings = Server_settings.query.all()
    if request.method == 'POST':
        button_pressed = request.form['button_pressed']
        if button_pressed == 'add':
            settings = Server_settings()
            settings.name = request.form['set_name']
            settings.value = request.form['set_value']
            settings.comment = request.form['set_comment']
            db.session.add(settings)
            db.session.commit()
            return redirect(url_for('ovpn_server_setup'))
#        elif button_pressed.find('edit_') != -1:
            # Edit button was pressed
#            set_name = button_pressed[button_pressed.find('edit_')+5:]
#            set_row = Server_settings.query.filter_by(name = set_name).first()
        elif button_pressed.find('delete_') != -1:
            # delete was pressed
            set_name = button_pressed[button_pressed.find('delete_')+7:]
            set_row = Server_settings.query.filter_by(name = set_name).first()
            db.session.delete(set_row)
            db.session.commit()
            return redirect(url_for('ovpn_server_setup'))
    return render_template('/ovpn/server_db_setup.html', all_settings = all_settings)