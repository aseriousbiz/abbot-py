import jsonpickle
import os
import re
import requests

from . import apiclient

class Geocode(object):
    """
    A Geocoded address.
    
    :var formatted_address: The formatted address returned by the geocoding service.
    :var time_zone_id: A human-readable time zone id, like `America/Los_Angeles`.
    :var latitude: The latitude of the geocoded address.
    :var longitude: The longitude of the geocoded address.
    """
    def __init__(self, coordinate, formatted_address, time_zone_id = None):
        self.formatted_address = formatted_address
        self.time_zone_id = time_zone_id
        self.latitude = coordinate.get("latitude")
        self.longitude = coordinate.get("longitude")
    
    def __repr__(self):
        return "Geocode: {} ({},{})".format(self.formatted_address, 
                                            self.latitude, 
                                            self.longitude)


class Utilities(object):
    """
    Utilities to make development more convenient with Abbot. 

    This has already been instantiated for you in ``bot.utils``.
    """
    def __init__(self, skill_id, user_id, api_token, timestamp):
        self.skill_id = skill_id
        endpoint_uri = os.environ.get('SkillApiBaseUriFormatString', 'https://localhost:4979/api/skills/{0}') 
        self.request_uri = endpoint_uri.format(self.skill_id)
        
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = apiclient.ApiClient(self.request_uri, user_id, api_token, timestamp)

    
    def geocode(self, address, include_timezone=False):
        """
        Geocode an address. 

        Args:
            address (str): the address to geocode.
            include_timezone (bool, optional): If True, include time zone information in the result. Defaults to False.
        """
        clean_address = requests.utils.requote_uri(address)
        uri = self.request_uri + "/geo?address={}&includeTimezone={}".format(clean_address, include_timezone)
        result = self.api_client.get(uri)
        # This will return an object that contains a string called Address, and an (int, int) tuple called Geocode 
        # representing the lat/lng of the point.
        # example:
        # {'timeZoneId': 'America/Los_Angeles', 
        #  'coordinate': {'latitude': 34.0692042, 'longitude': -118.4066574}, 
        #  'formattedAddress': '9663 S Santa Monica Blvd, Beverly Hills, CA 90210, USA'}
        g = Geocode(result.get("coordinate"), result.get("formattedAddress"), result.get("timeZoneId"))
        return g


    def __str__(self):
        return "Utilities object for {} skill.".format(self.skill)


    def __repr__(self):
        return "Utilities object for {} skill.".format(self.skill)
    

def camel_to_snake_case(input):
    """
    Convert CamelCase input to snake_cased output
    Taken from: https://stackoverflow.com/a/12867228/122117
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', input).lower()


class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, camel_to_snake_case(a), [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, camel_to_snake_case(a), obj(b) if isinstance(b, dict) else b)

    
    def __str__(self):
        return jsonpickle.dumps(self, unpicklable=False)