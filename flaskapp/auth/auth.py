import os
from flaskapp import app, db
from flask import redirect, request, flash, url_for, render_template
from werkzeug.security import check_password_hash
from flask_login import current_user, login_user , logout_user
from ..models.models import WebUser, init_WebUser_tabel

@app.route('/login', methods=('GET','POST'))
def login():
    if current_user.is_authenticated:
        flash("Already logged in as " + current_user.username, "primary")
    # checking if any users exist in WebUser table:
    if WebUser.query.all() == []:
        init_WebUser_tabel()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = WebUser.query.filter_by(web_username = username).first()
        if user == None:
            flash ("Web User : " + username + " does not exist.", 'danger')
            return redirect (url_for('login'))
        if check_password_hash(user.web_password_hash,password):
            # setting username
            user.sys_username = os.popen("whoami").read().strip()
            # reseting sudo password
            user.sudo_password_encoded = 'no sudo set'
            user.sudo_verified = False
            db.session.commit()
            # login user
            login_user(user,remember=False)
            flash("Welcome. Please Verify you 'sudo' password as first step.", "success")
            return redirect(url_for('sudo'))
        else:
            flash('Wrong Username or Password', "danger")
            return redirect (url_for('login'))
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
     user = WebUser.query.filter_by(id=current_user.id).first()
     if (current_user.is_authenticated):
        user.sys_username = 'no system user'
        user.sudo_password_encoded = 'no sudo set'
        user.sudo_verified = False
        db.session.commit()
        logout_user()
     else:
        flash ('Not login', "warning")
     return redirect(url_for('login'))

     