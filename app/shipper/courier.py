import os
import pathlib
import json
import time
import requests
from abc import ABC, abstractmethod  # For enforcing an interface


# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))


class Courier(ABC):
    def __init__(self, auth_url, client_id, client_secret, account_id):
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_id = account_id
        self.token = None
        self.token_expires_at = None



    def send_request(self, url, headers, payload):
        """Send a request to the API."""
        token = self.get_auth()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code not in [200, 201]:
            raise Exception(f"API request failed: {response.text}")
        return response.json()



    def dump_json(self, method, courier, file_name, _json):
        """Dump a json payload/response to the debug directory"""
        output_path = os.path.join(debug_dir, method, courier, file_name)
        with open(output_path, 'w') as f:
            json.dump(_json, f, indent=4)



    @abstractmethod
    def update_auth(self):
        """Abstract method for gaining auth"""
        pass



    @abstractmethod
    def quote_order(self, data):
        """Abstract method for quoting an order."""
        pass



    @abstractmethod
    def ship_order(self, data):
        """Abstract method for shipping an order."""
        pass



    @abstractmethod
    def void_order(self, data):
        """Abstract method for voiding an order."""
        pass
