from . import app

from flask import redirect, url_for, render_template, session, request
from flask_login import LoginManager, login_required, login_user, logout_user

from .models import user_manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(id):
    tmp_user = user_manager.get(id)
    if(tmp_user is None):
        return None
    else:
        return tmp_user

# handle login events from the user.
# This is an interactive version, though there will be a version which uses tokens
# to authenticate the backend as well later.
@app.route('/login', methods=['GET','POST'])
def login():
    if('account' in session):
        return redirect(url_for('home'))
    elif request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        check_user = user_manager.check(username, password)
        if(check_user != None):
            login_user(check_user, remember=('remember_me' in request.form))
            return redirect(request.args.get("next") or url_for("home"))
        else:
            # There was a fuckup.
            return render_template('login.html', error="Bad username or password", submitted_username=username, instance={})
        
        return "500"
    elif request.method == 'GET':
        # show login form
        return render_template('login.html', instance={})
    else:
        return "WTF?"

# Sometimes, you just forget things...
@app.route('/recover-account')
def recover_account():
    return "not implemented"

# Pop the user out and destroy their tokens. 
@app.route('/logout')
def logout():
    logout_user()
    # ayyy
    return redirect(url_for('home'))
