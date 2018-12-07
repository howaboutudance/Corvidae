from corvidae import app,db
from flask import url_for
import base36

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy_json import MutableJson, NestedMutableList

class Content(db.Model):
    """
    Content is the overarching "Type" within the timeline. Content is what constitutes a user's "timeline"

    When a user follows someone, their outbox is copied into the user's timeline (well, references to it, at least)
    When a user posts something, that content is placed into the user's timeline (and into the timelines of any followers)
    When a user likes something, that like is placed into the user's timeline (and into the timeline of the owner of the post)
    When a user reposts something, that repost reference is placed onto the user's timeline (and a notification is placed on the timeline of the user that posted the content, and quite possibly the user that reposted it previously,too)
    """

    __tablename__ = "content"
    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.DateTime)
    
    # from is always a solid reference (a specific point in the fediverse)
    actor = db.Column(db.Text)
    # To: is going to be a list. This somtimes includes us (e.g. DMs, mentions) but sometimes
    # is a vauge reference to __us__ (e.g. user/followers)
    to = db.Column(MutableJson)
    cc = db.Column(MutableJson)

    # This is the handle that this box item belongs to. . 
    handle_box = db.Column(db.Text, ForeignKey('handle.name'), nullable=False)
    handle = relationship('Handle', back_populates='timeline', order_by="Content.published")

    # this contains the URI of the Created, Announced, Liked or otherwise done-with object. 
    content_uri = db.Column(db.Text)
    # This should map 1:1 with ActivtyStream vocabulary, as seen in 
    # https://www.w3.org/TR/activitystreams-vocabulary/#activity-types
    # (though, we only support [create, announce, follow, like, flag])
    content_type = db.Column(db.Enum("Create","Announce","Like","Flag","Follow"))

    @property
    def id_url(self):
        return app.config["instance"]["base_url"] + "/status/"+self.base36_id

    @property
    def base36_id(self):
        """
        Base36 is used for external content. 
        """
        return base36.dumps(self.id)
    
    def from_base36(b36_id):
        un_base36 = base36.loads(b36_id)
        return Status.query.filter(Status.id == un_base36).one_or_None()


