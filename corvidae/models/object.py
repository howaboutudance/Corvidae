from corvidae import db

class Object(db.Model):
    id = db.Column(db.Inteer, primary_key=True)
    type = db.Column(db.Text)
    json_body = db.Column(db.Text)

    def get_json(self):
        # We're going to rehydrate the JSON references that are embedded in this 
        return json_body
