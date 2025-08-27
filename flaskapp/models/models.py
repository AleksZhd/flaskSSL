from flask_login import UserMixin
from flaskapp import login_manager, app, db


class OVPN_INFO(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name  = db.Column(db.String(30), unique = True)
    main_dir = db.Column(db.String(30), default = '/etc/openvpn/')
    main_dir_set = db.Column(db.Boolean, default = False)
    server_file = db.Column(db.String(30), default = 'server.conf')
    server_file_set = db.Column(db.Boolean, default = False)
    client_file = db.Column(db.String(30), default = 'client.conf')
    client_file_set = db.Column(db.Boolean, default = False)
    dh_file = db.Column(db.String(30), default = 'dh2048.pem')
    dh_file_set = db.Column(db.Boolean, default = False)
    ta_file = db.Column(db.String(30), default = 'ta.key')
    ta_file_set = db.Column(db.Boolean, default = False)


#        web_username = 'admin'
#        web_password_hash = 'scrypt:32768:8:1$PfyBG1m6XWvnUyZr$bb5f54cab05915b547aed319f45eee28618e27e42502909d38a256153f6fd89b9061fdbca0162856af2fbb7da8b2f6543fef2cae642f3e1b1af88c459126db9c'
class WebUser(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    web_username = db.Column(db.String(20), unique = True , nullable = False)
    web_password_hash = db.Column(db.String(200), nullable = False)
    sys_username = db.Column(db.String(20), default='no system user')
    sudo_password_encoded  = db.Column(db.String(100), default = 'no sudo set')
    sudo_verified = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f"WebUser('{self.web_username}', '{self.id}')"

#callback for load user 
@login_manager.user_loader
def load_user(user_id):
    return WebUser.query.filter_by(id=user_id).first()

#if WebUser is empty - fill it with default 'admin' value
def init_WebUser_tabel():
    user = WebUser.query.filter_by(web_username = 'admin').first()
    if not user:
        user = WebUser()
        user.web_username = 'admin'
        user.web_password_hash = 'scrypt:32768:8:1$PfyBG1m6XWvnUyZr$bb5f54cab05915b547aed319f45eee28618e27e42502909d38a256153f6fd89b9061fdbca0162856af2fbb7da8b2f6543fef2cae642f3e1b1af88c459126db9c'
        db.session.add(user)
        db.session.commit()