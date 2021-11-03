import json

class Mention(object):
    """
    A user mention.

    :var id: The user's Id.
    :var user_name: The user's user name.
    :var name: The user's name.
    :var email: The user's email if known
    :var location: The user's location if known.
    :var timezone: The user's timezone if known
    """
    def __init__(self, id, user_name, name, email, location, timezone):
        self.id = id
        self.user_name = user_name
        self.name = name
        self.email = email
        self.location = location
        self.timezone = timezone


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def __repr__(self):
        return "<@{}>".format(self.user_name) 

    def __str__(self):
        return "<@{}>".format(self.user_name)