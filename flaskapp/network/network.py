from flask import render_template
from flask_login import login_required
from flaskapp.network.network_lib import get_network_info, get_netstat_info
from flaskapp import app


@app.route("/network", methods = ['GET','POST'])
@login_required
def network():
    output_text = []
    output_text = get_network_info()
    return render_template("network/network.html", output_text = output_text)

@app.route("/netstat", methods = ['GET','POST'])
@login_required
def netstat():
    output_text = []
    output_text = get_netstat_info()
    return render_template("network/network.html", output_text = output_text)