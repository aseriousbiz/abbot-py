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


    @staticmethod
    def load_mentions(mentions_json):
        return [Mention.from_json(m) for m in mentions_json]


    @classmethod
    def from_json(cls, mention_json):
        if mention_json is None:
            return None
        location_arg = mention_json.get('Location')
        timezone_arg = mention_json.get('TimeZone')
        location = Location.from_json(location_arg)
        timezone = TimeZone.from_json(timezone_arg)
        # Special case for PlatformUser mentions
        if (location_arg is not None and timezone is None):
            tz_id = location_arg.get('TimeZoneId')
            if tz_id is not None:
                timezone = TimeZone(tz_id)
        return cls(mention_json.get('Id'), mention_json.get('UserName'), mention_json.get('Name'), mention_json.get('Email'), location, timezone)


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


    def __repr__(self):
        return "<@{}>".format(self.user_name) 


    def __str__(self):
        return "<@{}>".format(self.user_name)


class Coordinate(object):
    """
    Represents a geographic coordinate.

    :var latitude: The latitude. Those are the lines that are the belts of the earth.
    :var longitude: The longitude. Those are the pin stripes of the earth.
    """
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude


    @classmethod
    def from_json(cls, coordinate_json):
        if coordinate_json is None:
            return None
        return cls(coordinate_json.get('Latitude'), coordinate_json.get('Longitude'))


    def __str__(self):
        return "lat: {}, lon: {}".format(self.latitude, self.longitude)


class Location(object):
    """
    A geo-coded location

    :var coordinate: The coordinates of the location.
    :var formatted_address: The formatted address of the location.
    """
    def __init__(self, coordinate, formatted_address):
        self.coordinate = coordinate
        self.formatted_address = formatted_address


    @classmethod
    def from_json(cls, location_json):
        if location_json is None:
            return None
        coordinate_arg = location_json.get('Coordinate')
        coordinate = Coordinate.from_json(coordinate_arg)
        return cls(coordinate, location_json.get('FormattedAddress'))


    def __str__(self):
        return "coordinate: {}, address: {}".format(self.coordinate, self.formatted_address)


class TimeZone(object):
    """
    Information about a user's timezone

    :var id: The provider's ID for the timezone. Could be IANA or BCL.
    :var min_offset: Gets the least (most negative) offset within this time zone, over all time.
    :var max_offset: Gets the greatest (most positive) offset within this time zone, over all time.
    """
    def __init__(self, id, min_offset=None, max_offset=None):
        self.id = id
        self.min_offset = min_offset
        self.max_offset = max_offset


    @classmethod
    def from_json(cls, tz_json):
        if tz_json is None:
            return None
        return cls(tz_json.get('Id'), tz_json.get('MinOffset'), tz_json.get('MaxOffset'))


    def __str__(self):
        return self.id