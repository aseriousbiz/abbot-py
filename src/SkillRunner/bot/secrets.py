from .urls import get_skill_api_url

class Secrets(object):
    """
    Abbot's secrets manager. 

    This is automatically instantiated for you as ``bot.secrets``.
    """
    def __init__(self, api_client, skill_id):
        self._skill_id = skill_id
        self._request_uri = get_skill_api_url(skill_id) + '/secret?key={0}'
        self._api_client = api_client


    def read(self, key):
        """
        Read a secret from the vault. 

        Args: 
            key (str): The key of the secret to retrieve.
        
        Returns: 
            secret (str): The secret from the vault.
        """
        uri = self._request_uri.format(key)
        output = self._api_client.get(uri)
        if output:
            return output.get("secret")
        else:
            return None


    def test(self, key):
        return "You requested a secret called '{}'.".format(key)
    

    def __str__(self):
        return "Secret store for {} skill.".format(self._skill_id)


    def __repr__(self):
        return "Secret store for {} skill.".format(self._skill_id)