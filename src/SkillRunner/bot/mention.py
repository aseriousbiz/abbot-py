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


    @classmethod
    def from_json(cls, mention_arg):
        if mention_arg is None:
            return None
        location_arg = mention_arg.get('Location')
        timezone_arg = mention_arg.get('TimeZone')
        location = Location.from_json(location_arg)
        timezone = TimeZone.from_json(timezone_arg)
        # Special case for PlatformUser mentions
        if (location_arg is not None and timezone is None):
            tz_id = location_arg.get('TimeZoneId')
            if tz_id is not None:
                timezone = TimeZone(tz_id)
        return cls(mention_arg.get('Id'), mention_arg.get('UserName'), mention_arg.get('Name'), mention_arg.get('Email'), location, timezone)


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
    def from_json(cls, coordinate_arg):
        if coordinate_arg is None:
            return None
        return cls(coordinate_arg.get('Latitude'), coordinate_arg.get('Longitude'))


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
    def from_json(cls, location_arg):
        if location_arg is None:
            return None
        coordinate_arg = location_arg.get('Coordinate')
        coordinate = Coordinate.from_json(coordinate_arg)
        return cls(coordinate, location_arg.get('FormattedAddress'))


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
    def from_json(cls, tz_arg):
        if tz_arg is None:
            return None
        return cls(tz_arg.get('Id'), tz_arg.get('MinOffset'), tz_arg.get('MaxOffset'))


    def __str__(self):
        return self.id