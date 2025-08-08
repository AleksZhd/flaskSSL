import os
from flaskapp import db
from flaskapp.sudo.sudo_lib import sudo_timestemp_reset
from flaskapp.models.models import OVPN_INFO


class OVPN_info:
    main_dir = '/etc/openvpn'
    server_conf = 'server.conf'
    client_conf = 'client.conf'
    dh_file = 'dh2048.pem'
    ta_file = 'ta.key'

def get_ovpn_config(id=1):
    error = 'NONE'
    if not sudo_timestemp_reset():
        error = 'Please check/reset SUDO password'
        return error
# init table in DataBase if no records found    
    OVPN = OVPN_INFO.query.filter_by(id = id).first()
    if not OVPN:
        OVPN = OVPN_INFO()
        OVPN.name = 'Default OVPN'
        db.session.add(OVPN)
        db.session.commit()