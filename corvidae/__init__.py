# Corvidae
# a multi-user multi-whatever ActivityPub server

from flask import Flask, render_template, session, redirect, request
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


# Configuration stuff
# We want the environment path CORVIDAE_INSTANCE_PATH to point to a directory

if None == os.getenv("CORVIDAE_INSTANCE_PATH", None):
    import sys
    print("Path to instance data not set, please set CORVIDAE_INSTANCE_PATH")
    sys.exit(-1)
else:
    instance_path = os.getenv('CORVIDAE_INSTANCE_PATH')
    import toml
    # get the dictionary out
    # We want to include some default stuff in there too
    default_path = os.path.join(os.path.dirname(__file__), "defaults.toml")
    print(f"defaults stored at {default_path} instance stored at {instance_path}")
    toml_conf_dict = toml.load( [default_path, os.path.join(instance_path, 'instance.toml')] )
    for k,v in toml_conf_dict.items():
        app.config[k] = v
    # And now we just want to make sure that the instance path is remembered
    app.config['INSTANCE_PATH'] = instance_path
    if not 'DATA_PATH' in app.config:
        app.config['DATA_PATH'] = os.path.join(instance_path, 'data')
    if not 'CACHE_PATH' in app.config:
        app.config['CACHE_PATH'] = os.path.join(instance_path, 'cache')
    if 'DATABASE_URI' in app.config:
       # Set up SQLAlchemy with that
       app.config['SQLALCHEMY_DATABASE_URI'] = app. config['DATABASE_URI']
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{instance_path}/corvidae.db"

# Now we can initialize the DB. 
db  = SQLAlchemy(app)

import corvidae.models

# Snagged from Pylodon: This handles some silliness that Activipy creates
@app.before_request
def add_at_prefix():
    if request.content_type != 'application/activitypub+json':
        return
    else:
        r = request.get_json()
        if r is not None:
            keys = ['id', 'type']
            for key in keys:
                if r.get(key, False):
                    r['@'+key] = r.pop(key)


@app.route("/")
def home():
    if(current_user.is_authenticated):
        return card_home()
    else:
        return render_template('index-anon.html', instance={})

from flaskext.markdown import Markdown

Markdown(app)

@app.route('/about')
def about_instance():
    # get the content out of DATA_PATH
    return ""


@app.route('/timeline')
def card_home():
    return render_template('index.html',
    page={
        "title":"Card Stream",
        "css": ['css/cardstream.css']
    },
    instance={}
    )

from . import auth
