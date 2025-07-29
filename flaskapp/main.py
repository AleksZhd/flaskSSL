from flaskapp import app
from flask import redirect, render_template, url_for, flash
from flask_login import current_user

@app.route("/")
def index():
    if not current_user.is_authenticated:
        flash ("Please Login", "warning")
        return redirect(url_for('login'))
    return render_template('index.html')