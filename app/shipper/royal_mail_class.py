from app.shipper.courier import Courier
import os
import pathlib
from dotenv import load_dotenv

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))

# load env variables and set if using live or test
load_dotenv()
prefix = 'TEST_'
# prefix = ''


class RoyalMail(Courier):
    def __init__(self):
        super().__init__(
            auth_url = os.getenv(f'{prefix}RM_OAUTH_URL'),
            client_id = os.getenv(f'{prefix}RM_ID'),
            client_secret = os.getenv(f'{prefix}RM_SECRET'),
            account_id = os.getenv(f'{prefix}RM_ACCOUNT_ID')
        )
        self.quote_url = os.getenv(f'{prefix}RM_QUOTE_URL')
        self.ship_url = os.getenv(f'{prefix}RM_QUOTE_URL')
        self.void_url = os.getenv(f'{prefix}RM_VOID_URL')


    def quote_order(self, data):
        """RoyalMail-specific logic for quoting an order."""
        # Format payload specific to RoyalMail
        payload = {"example_field": data["field"]}
        response = self.send_request(self.quote_url, payload)
        return response


    def ship_order(self, data):
        """RoyalMail-specific logic for shipping an order."""
        # Format payload specific to RoyalMail
        payload = {"example_field": data["field"]}
        response = self.send_request(self.ship_url, payload)
        return response