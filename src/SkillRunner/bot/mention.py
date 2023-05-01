from .working_hours import WorkingHours

import json

from .chat_address import ChatAddress, ChatAddressType
from .platform_type import PlatformType

class UserMessageTarget(object):
    """
    A user message target is a handle that can be used to send messages to that user.

    :var id: The user ID.
    """
    def __init__(self, id):
        self.id = id

    def get_chat_address(self):
        return ChatAddress(ChatAddressType.USER, self.id)

    def get_thread(self, thread_id: str):
        """
        Gets a handle to the specified thread in this user's DMs with Abbot.

        Args:
            thread_id (str): The platform-specific thread ID.
        """
        return ChatAddress(ChatAddressType.USER, self.id, thread_id)


class Mention(UserMessageTarget):
    """
    A user mention.

    :var id: The user's Id.
    :var user_name: The user's user name.
    :var name: The user's name.
    :var email: The user's email if known
    :var location: The user's location if known.
    :var timezone: The user's timezone if known
    :var platform_type: The platform type of the user.
    :var working_hours: The working hours of the user.
    """
    def __init__(self, id, user_name, name, email, location, platform_type=None, working_hours=None):
        super().__init__(id)
        self.user_name = user_name
        self.name = name
        self.email = email
        self.location = location
        self.__platform_type = platform_type
        self.working_hours = working_hours

    def __eq__(self, other):
        return isinstance(other, Mention) and \
            self.id == other.id and \
            self.user_name == other.user_name and \
            self.name == other.name and \
            self.email == other.email and \
            self.location == other.location and \
            self.__platform_type == other.__platform_type

    @property
    def timezone(self):
        return self.location.timezone if self.location is not None else None

    @staticmethod
    def load_mentions(mentions_json, platform_type=None):
        if mentions_json is None:
            return []
        else:
            return [Mention.from_json(m, platform_type) for m in mentions_json]

    @classmethod
    def from_json(cls, mention_json, platform_type=None):
        if mention_json is None:
            return None
        location_arg = mention_json.get('Location')
        location = Location.from_json(location_arg)

        if location is None or location.timezone is None:
            timezone_arg = mention_json.get('TimeZone')
            timezone = TimeZone.from_json(timezone_arg)
            if timezone is None:
                tz_id = mention_json.get('TimeZoneId')
                if tz_id is not None:
                    timezone = TimeZone(tz_id)

            if location is None:
                location = Location(None, None, timezone)
            else:
                location.timezone = timezone
        working_hours = WorkingHours.from_json(mention_json.get('WorkingHours'))
        return cls(
            mention_json.get('Id'),
            mention_json.get('UserName'),
            mention_json.get('Name'),
            mention_json.get('Email'),
            location,
            platform_type,
            working_hours)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"<at>{self.name}</at>" if self.__platform_type == PlatformType.MS_TEAMS \
            else f"<@{self.id}>"


class Coordinate(object):
    """
    Represents a geographic coordinate.

    :var latitude: The latitude. Those are the lines that are the belts of the earth.
    :var longitude: The longitude. Those are the pin stripes of the earth.
    """
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __eq__(self, other):
        return isinstance(other, Coordinate) and \
            self.latitude == other.latitude and \
            self.longitude == other.longitude

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
    def __init__(self, coordinate, formatted_address, timezone):
        self.coordinate = coordinate
        self.formatted_address = formatted_address
        self.__timezone = timezone

    @property
    def timezone(self):
        return self.__timezone
    
    @timezone.setter
    def timezone(self, val):
        self.__timezone = val

    def __eq__(self, other):
        return isinstance(other, Location) and \
            self.coordinate == other.coordinate and \
            self.formatted_address == other.formatted_address and \
            self.__timezone == other.__timezone

    @classmethod
    def from_json(cls, location_json):
        if location_json is None:
            return None
        coordinate_arg = location_json.get('Coordinate')
        coordinate = Coordinate.from_json(coordinate_arg)

        timezone_arg = location_json.get('TimeZone')
        if timezone_arg is None:
            id = location_json.get('TimeZoneId')
            timezone = TimeZone(id) if id is not None else None
        else:
            timezone = TimeZone.from_json(timezone_arg)

        return cls(coordinate, location_json.get('FormattedAddress'), timezone)

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

    def __eq__(self, other):
        return isinstance(other, TimeZone) and \
            self.id == other.id and \
            self.min_offset == other.min_offset and \
            self.max_offset == other.max_offset

    @classmethod
    def from_json(cls, tz_json):
        if tz_json is None:
            return None
        if isinstance(tz_json, str):
            return cls(tz_json)
        if isinstance(tz_json, dict):
            return cls(tz_json.get('Id'), tz_json.get('MinOffset'), tz_json.get('MaxOffset'))

        return None

    def __str__(self):
        return self.id
        
    def __eq__(self, other):
        return self.id == other.id and self.min_offset == other.min_offset and self.max_offset == other.max_offset