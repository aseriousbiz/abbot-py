import urllib.parse
import logging

from SkillRunner.bot.room import RoomIdentifier

class CustomersClient():
    """
    Used to manage customers.
    """
    def __init__(self, api_client):
        self._api_client = api_client
        self.logger = logging.getLogger("CustomerClient")

    def get_all(self):
        """
        Gets all the customers.
        """
        customers_json = self._api_client.get("/customers")
        return [Customer.from_json(customer_json) for customer_json in customers_json]

    def get(self, id: int):
        """
        Gets a customer by id.
        """
        url = f"{self.__customer_url(id)}"
        customer_json = self._api_client.get(url)
        return Customer.from_json(customer_json)
    
    def get_by_name(self, name):
        """
        Gets a customer by name.
        """
        url = f"{self.__customer_url()}/name/{urllib.parse.quote(name)}"
        customer_json = self._api_client.get(url)
        return Customer.from_json(customer_json)

    def create(self, customer: 'CustomerRequest'):
        """
        Creates a customer.
        """
        url = f"{self.__customer_url()}"
        body = customer.to_json()
        customer_json = self._api_client.post(url, body)
        return Customer.from_json(customer_json)

    def update(self, id, customer: 'CustomerRequest'):
        """
        Creates a customer.
        """
        url = f"{self.__customer_url(id)}"
        body = customer.to_json()
        customer_json = self._api_client.put(url, body)
        return Customer.from_json(customer_json)

    def __customer_url(self, id=None):
        """
        Returns the URL for a Customer.

        Args:
            id (int): The id of the customer to get the URL for.

        Returns:
            str: The URL for the customer.
        """
        return "/customers" if id is None else f"/customers/{urllib.parse.quote_plus(str(id))}"

class CustomerRequest():
    """
    Information about a customer to create.

    :var id: The database id of the customer.
    :var name: The name of the customer.
    :var rooms: The channels to add the customer to.
    :var tags: (optional) The set of tags to attach to the customer.
    """
    def __init__(self, name, rooms, tags=None):
        self.name = name
        self.rooms = rooms
        self.tags = tags

    @classmethod
    def from_json(cls, customer_json):
        """
        Creates a Customer from a JSON representation.
        """
        name = customer_json.get('name')
        rooms = [RoomIdentifier.from_json(room_json) for room_json in customer_json.get('rooms')]
        tags = customer_json.get('tags')
        return cls(name, rooms, tags)

    def to_json(self):
        """
        Returns a JSON representation of this object.
        """
        return {
            "Name": self.name,
            "Rooms": self.rooms,
            "Tags": [] if self.tags is None else self.tags
        }

class Customer(CustomerRequest):
    """
    Information about a customer.

    :var id: The database id of the customer.
    :var name: The name of the customer.
    :var rooms: The channels to add the customer to.
    :var tags: (optional) The set of tags to attach to the customer.
    """
    def __init__(self, id:int, name, rooms, tags=None):
        super().__init__(name, rooms, tags)
        self.id = id

    def to_json(self):
        """
        Returns a JSON representation of this object.
        """
        return {
            "Id": self.id,
            "Name": self.name,
            "Rooms": self.rooms,
            "Tags": [] if self.tags is None else self.tags
        }

    @classmethod
    def from_json(cls, customer_json):
        """
        Creates a Customer from a JSON representation.
        """
        id = customer_json.get('id')
        name = customer_json.get('name')
        rooms = [RoomIdentifier.from_json(room_json) for room_json in customer_json.get('rooms')]
        tags = customer_json.get('tags')
        return cls(id, name, rooms, tags)
