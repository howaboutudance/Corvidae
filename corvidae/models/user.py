from .shelfmanager import ShelfManager as ShelfManager
from .. import app
from activipy import vocab as ASVocab

from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship

class User(db.Model):
    """
    The User class holds information about a specific user.
    """

    __tablename__='user'

    username = Column(Text, primary_key=True, unique=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, unique=False, nullable=False)
    db_flags = Column(Text)
    totp_key = Column(Text)
    handles = relationship('Handle',back_populates='owner')

    @property(setter=set_flags)
    def flags(self):
        split_flags = map( lambda k: k.strip(),  self.db_flags.split(';') )
        return set(split_flags)
    def set_flags(self, flag_arr):
        set_flags = set(flag_arr)
        sel.db_flags = ';'.join(set_flags)

    def set_flag(self, flag, state):
        fl = self.flags
        if state:
            fl.add(flag)
        else:
            fl.remove(flag)
        self.flags = fl
    
    def get_id(self):
        return self.username
    
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

class Handle(db.Model):
    __tablename__='handle'
    id = db.Column(db.Integer, primary_key=True)
    # Name is some "@-name" -- bob, sally, etc. 
    # This is the "local part" of an acct: URI. 
    name = db.Column(db.Text,  unique=True, nullable=False)
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
    owner_id = db.Column(db.Integer, ForeignKey('user.username'), nullable=True)
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


class FollowState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    following_handle = db.Column(db.Integer, ForeignKey('handle.name'))
    follower = relationship('Handle', back_populates='following')
    # This is an IRI that should be looked at. 
    followed = db.Column(db.Text, ForiegnKey('handle.name'))
    following = relaitonship('Handle', back_populates='followed_by')
    approved = db.Column(db.Boolean)