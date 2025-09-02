from flaskapp import app, db

class Server_settings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), default = ';')
    value = db.Column(db.String(50), default  = '')
    comment = db.Column(db.String(50), default  = '')
    