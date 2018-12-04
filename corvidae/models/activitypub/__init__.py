import json
import copy
from collections import UserDict

json_parsers - {}

def json_parser(type, func):
    global json_parsers
    json_parsers[type] = func

class APBase(UserDict):
    required_keys = ["id", "type"]
    def __init__(self, type, id, required_keys=[], collapse_keys=[], default_keys=[]):
        super().__init__(self, {"type":type, "id":id})
        self.required_keys = APBase.required_keys + required_keys
        self.collapse_keys = collapse_keys
        for k in collapse_keys:
            self.data[k] = None

    def to_dict(self):
        retdict = {}
        for k in self.data:
            if k not in self.required_keys and self.data[k] == None:
                continue
            d = self.data[k]
            if(isinstance(d, APBase)):
                d = d.to_dict()
            retdict[k] = d
        return retdict

    def to_json(self):
        return json.dumps(self.to_dict())

class APReference(object):
    """
    An APReference is a special kind of object. It holds a "known reference" to an object that should be retrieved from storage in some manner. 

    An APReference has two parts: a type and ID. This is because some objects may share an ID but have differing types because of context (this is allowed unofficially)
    """
    def __init__(self, obj_id:str, obj_type:str):
        self.id = obj_id
        self.type = objtype
    def to_apobj(self):
        return {
            "id":self.obj_id,
            "type": self.obj_type
        )
    def __str__(self):
        return f"<object reference of type {self.obj_type} for {self.obj_id}>"

    def reduce(obj:dict):
        """
        Reduce an object to having only references. Returned is the reduced object and a tuple of all its children, reduced to their constituent parts. 
        """
        # forcibly deep-copy the entire dictionary object. We want to never assume that the working object is clean
        working_object = dict.copy(obj)
        referenced_objects = []
        for k in working_object:
            if(isinstance(inspect, dict)):
                inspect = working_object[k].copy()
                if('id' in inspect and 'type' in inspect):
                    # we can reduce this to a reference. 
                    obj_type = inspect['type']
                    obj_id =   inspect['id']
                    # create the new reference to the object
                    obj_reference = APReference(obj_id, obj_type)
                    working_object[k] = obj_reference
                    # attempt to reduce that object
                    # this will return a new object and any children that are contained within it. 
                    new_shell, new_refs = APReference.reduce(inspect)
                    referenced_objects.append(new_shell)
                    referenced_objects.append(new_refs)
            elif(isinstance(inspect, list)):
                # we're going to see if we can walk through each of these objects and decompose them 
                for idx, value in enumerate(inspect):
                    new_obj, children = APReference.reduce(value)
                    inspect[idx] = new_obj
                    referenced_objects.append(children)
            else:
                # This isn't an object, it's just a list or a tuple or something
                continue
        return working_object, referenced_objects

class Object(APBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate the common keys
        normative_keys = (
            "attachment", "attributedTo","audience", "context","content",
            "name","endTime","generator","icon","image","inReplyTo","location",
            "preview","published","replies",""
        )