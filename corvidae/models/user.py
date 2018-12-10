from .. import app, db
from activipy import vocab as ASVocab

from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy_json import MutableJson

class User(db.Model):
    """
    The User class holds information about a specific user.
    """

    __tablename__='user'
    id       = Column(Integer, primary_key=True, unique=True)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, unique=False, nullable=False)
    db_flags = Column(MutableJson) # should enforce this as being an array.
    totp_key = Column(Text)
    handles = relationship('Handle',back_populates='owner')

    def get_id(self):
        return self.id
    
    # this is for flask-login
    @property
    def is_active(self):
        if('suspended' in self.flags):
            return False
        else:
            return True
    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
import re 

class Handle(db.Model):
    __tablename__='handle'
    id = db.Column(db.Integer, primary_key=True)
    # Name is some "@-name" -- bob, sally, etc. 
    # This is the "local part" of an acct: URI. 
    name = db.Column(db.Text,  unique=True, nullable=False)

    @validates('name')
    def check_name(self, key, name):
        check_re = re.compile('[a-zA-Z0-9_-]')
        if(not re.match(name)):
            raise AssertionError()
        else:
            return name

    # This is the full acct: uri
    acct = db.Column(db.Text,  nullable=True, default="acct:")
    is_external = db.Column(db.Boolean, nullable=False, default=False)
    # This contains the results from WebFinger, plus some other stuff. 
    external_json_cache = db.Column(db.Text, nullable=True, default="{}")
    # This defines when we last fetched this user when they were last asked for.
    # in app.config<cache><external_json_fetch> we should define how long we should 
    # cache the JSON data for. 
    external_json_fetched  = db.Column(db.DateTime)
    # The display name of the handle
    display_name = db.Column(db.Text)
    # Who owns the handle (NULL if external)
    owner_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    # owner User of the handle. This has no guarantees if the user itself is actually
    # associated with a local user. 
    owner = relationship('User', back_populates='handles')
    # Fully qualified URL of the banner image 
    banner_url = db.Column(db.Text, nullable=True)
    # Fully qualified URL of the handle's Icon 
    icon_url   = db.Column(db.Text, nullable=True)
    # Some text about this handle.
    summary  = db.Column(db.Text)
    # If this user is a bot, say so.
    is_bot = db.Column(db.Boolean, default=False)
    # This user needs to confirm follows
    follow_confirm = db.Column(db.Boolean, default=False)
    # If this user is already following a person who is requesting a follow,
    # Auto Mutual will auto-accept the follow itself. 
    autoconfirm_mutual = db.Column(db.Boolean, default=False)

    # This is for header signing. It contains sensitive data, just like the user TOTP. 
    secret_key_b64 = db.Column(db.Text)

    @property
    def sk_bytes(self):
        import base64
        return base64.b64decode(self.secret_key_b64)
    




class FollowState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    following_handle = db.Column(db.Integer, ForeignKey('handle.name'))
    follower = relationship('Handle', back_populates='following')
    # This is an IRI that should be looked at. 
    followed = db.Column(db.Text, ForeignKey('handle.name'))
    following = relationship('Handle', back_populates='followed_by')
    approved = db.Column(db.Boolean)