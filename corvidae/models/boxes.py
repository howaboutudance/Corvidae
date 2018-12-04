from .shelfmanager import ShelfManager
from .. import app
from activipy import vocab as ASVocab


class OutboxManager(ShelfManager):
    def __init__(self, app):
        super().__init__(app, "outboxes")
    def get(self, id):
        # Check that the id matches a handle.
        handle = handle_manager.get_handle(id)
        if(handle == None):
            # No user or handle of that name exists.
            # Return None
            return None
        else:
            # See if it exists.
            outbox = self.shelf.get(handle.name)
            return outbox
    def add_object(self, obj:ASVocab.Object ):
        # obj is going to be a complete ASObject
        # We need to denormalize it and find the appropriate place to put things.
        
        

        pass

    @app.route("/oubox/<handle>")
    def render_outbox(handle):
        # Turn the items into a 
        pass

class InboxManager(ShelfManager):
    def __init__(self, app):
        super().__init__(app, "inboxes")
    def get(self, id):
        return None
    
    @app.route("/inbox/<handle>")
    def render_inbox(handle):
        return "[]"


class Box(object):
    def __init__(self, handle, items=[]):
        self.owner = handle
        self.items = items
    
    def get_owner_handle(self):
        return handle_manager.get_handle(self.owner)
    def get_owner_account(self):
        return handle_manager.get_owner_account(self.get_owner_handle)
    def get_items(self, max=None, offset=0, filter=lambda x:x):
        
        ret = []
        if(max == None): 
            max = len(self.items)
        id_index = offset
        max_idx = min(len(self.items), offset + max)
        while( len(ret) < max and id_index <= max_idx ):
            tmp_obj = object_manager.get(self.items[id_index])
            if(tmp_obj != None and filter(tmp_obj)):
                ret.append(tmp_obj)
            id_index += 1
        return ret
