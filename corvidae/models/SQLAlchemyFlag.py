import sqlalchemy.types as types
import json

class SQLFlagType(types.TypeDecorator):
    """
    An SQLFlagType is a wrapper around strings. Internally, it's a JSON array.
    """
    impl = types.Text

    def process_bind_param(self, value, dialect):
        """
        Make sure that the input is a set
        """
        if not isinstance(value, (set, list, tuple):
            # bail
            raise ArgumentError("Value is of invalid type:"+repr(value))
        
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        # value coming in is a JSON string
        return set(json.loads(value))
