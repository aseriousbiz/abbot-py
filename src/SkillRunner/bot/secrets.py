import urllib.parse

class Secrets(object):
    """
    Abbot's secrets manager. 

    This is automatically instantiated for you as ``bot.secrets``.
    """
    def __init__(self, api_client):
        self._api_client = api_client

    def read(self, key):
        """
        Read a secret from the vault. 

        Args: 
            key (str): The key of the secret to retrieve.
        
        Returns: 
            secret (str): The secret from the vault.
        """
        output = self._api_client.get(f"/secret?key={urllib.parse.quote_plus(key)}")
        if output:
            return output.get("secret")
        else:
            return None

    def __str__(self):
        return "Secret store for skills."

    def __repr__(self):
        return "Secret store for skills."