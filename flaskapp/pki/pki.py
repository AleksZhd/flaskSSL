from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from flaskapp import app
from flaskapp.pki.pki_lib import delete_pki, dir_tree, make_dir, get_pki_dir, update_pki_dir
from flaskapp.sys_lib import file_to_list


@app.route('/pki' , methods =['GET', 'POST'])
@login_required
def pki():
# GET
    if not current_user.sudo_verified:
        flash ("No sudo password!",'warning' )
        return redirect(url_for('sudo'))
    error, pki_dir = get_pki_dir()
    if error != 'NONE':
        flash (error, 'danger')
        return ('System Error')    
    dir_list = dir_tree (pki_dir, False)
    dir_files_list = dir_tree (pki_dir, True)
    # index_list = ['','']
    error, index_list = file_to_list (pki_dir + '/RootCA/DataBase/index.txt')
#    if error != 'NONE':
#       flash (error , 'danger')
# POST
    if request.method == 'POST':
        directory_name = request.form['main_directory']
        if directory_name == '':
            directory_name = pki_dir
        update_pki_dir(directory_name)
        if request.form['button_pressed'] == 'create':
            make_dir(directory_name)
            return redirect (url_for ("pki"))
        elif request.form['button_pressed'] == 'delete':
            delete_pki(directory_name)
            return redirect (url_for ("pki"))
        elif request.form['button_pressed'] == 'view':
            return redirect (url_for ("pki"))
        
    return render_template('pki/pki.html', 
                           pki_dir = pki_dir, 
                           dir_list = dir_list, 
                           dir_files_list = dir_files_list, 
                           index_list = index_list)