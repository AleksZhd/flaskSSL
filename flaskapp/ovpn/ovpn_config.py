from flask import redirect, render_template, flash, request, url_for
from flask_login import login_required
from flaskapp.models.models import OVPN_INFO
from flaskapp import app, db
from flaskapp.ovpn.ovpn_lib import get_ovpn_config, get_ovpn_tree, install_ovpn, create_files

@app.route('/ovpn_config', methods  = ['POST' , 'GET'])
@login_required
def ovpn_config():
    error = get_ovpn_config()
    if error != 'NONE':
        flash(error, 'danger')
    ovpn = OVPN_INFO.query.filter_by(id = 1).first()
    error, ovpn_tree = get_ovpn_tree(id=1)
# POST
    if  request.method == 'POST':
# install openvpn button:
        if request.form['button_pressed'] == 'install_ovpn':
            error = install_ovpn()
            if error != 'NONE':
                flash (error, 'danger')
            return redirect (url_for('ovpn_config'))

        if request.form['button_pressed'] == 'create_files':
            error = create_files()
            if error != 'NONE':
                flash (error, 'danger')
            return redirect (url_for('ovpn_config'))
        
        if request.form['button_pressed'] == 'set_server_file' and request.form['server_file'] != '':
            ovpn.server_file = request.form['server_file']
            db.session.commit()
            return redirect (url_for('ovpn_config'))
 
        if request.form['button_pressed'] == 'set_client_file' and request.form['client_file'] != '':
            ovpn.client_file = request.form['client_file']
            db.session.commit()
            return redirect (url_for('ovpn_config'))

 #       if request.form['button_pressed'] == 'view_server_file':
  #          return redirect (url_for('view_file', file = 'server_file'))

    return render_template ('/ovpn/ovpn_config.html', ovpn = ovpn, ovpn_tree = ovpn_tree )

#@app.route('/file/<file>', methods = ['GET' , 'POST'])
#@login_required
#def view_file(file):
#    ovpn = OVPN_INFO.query.filter_by(id = 1).first()
#    file_path = ovpn.main_dir + 
#    text = open(file).read()
#    if request.method == 'POST':
#        text = request.form['text']
#        file = open('config','w')
#        file.write(text)
#        file.close()
 
#    return render_template('/file.html', text = text )