import requests
import json
import os
import pathlib
from dotenv import load_dotenv
import re
from pgeocode import Nominatim
from app.shipper import shipping_functions
from app.logger import update_log

# database
from app import db
from app.models import Countries


prefix='TEST_'


# load .env variables
load_dotenv()
api_base_url = os.getenv(f'{prefix}ODOO_API_BASE_URL')
main_headers = {"api_key": os.getenv(f'{prefix}ODOO_API_KEY')}


# vars
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))


###########################################################################################################################################

###########################################################################################################################################
# Helper functions for general use


def join_url(*url_parts):
    """
    Simple function to join all parts of the passed in url pieces and return
    This is because os.path.join doesnt work for URLs and i didnt want to muck about with other libraries when this is just as easy
    """
    url_parts = map(str, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url


###########################################################################################################################################

###########################################################################################################################################
# Functions for getting all orders


def get_valid_orders(content):
    # loop over the content and check if the order wants to be completed
    valid_orders = []
    for order in content:
        status = order.get('picking_stage', 'no')

        # if the status wants to be processed then add it to the valid_orders list
        if status not in ['no', 'waiting', 'packed']:
            valid_orders.append(order)
    return valid_orders


def get_orders():
    """Request all current orders and return the first one that wants to be processed."""

    # build url and query it
    url = join_url(api_base_url, 'dwapi', 'orders')
    res = requests.get(url, headers=main_headers, json={})
    data = res.json()

    # dump response for debugging
    with open(os.path.join(debug_dir, 'orders', 'all_orders_dump.json'), 'w') as f:
        json.dump(data, f, indent=4)

    # handle response
    if res.status_code == 200:
        valid_orders = get_valid_orders(data['result'])
        if valid_orders:
            return {
                'state': 'Success',
                'value': valid_orders
            }
        else:
            return {
                'state': 'Error',
                'value': 'No valid orders'
            }

    else:
        return {
            'state': 'Error',
            'value': data['error']
        }


###########################################################################################################################################
# Functions for searching a specific order id


def get_specific_order(order_id):
    """Search for a specific order id and return all the data"""

    # build url and query it
    url = join_url(api_base_url, 'dwapi', 'order', order_id)
    res = requests.get(url, headers=main_headers, json={})
    data = res.json()

    # dump response for debugging
    with open(os.path.join(debug_dir, 'orders', 'order_dump.json'), 'w') as f:
        json.dump(data, f, indent=4)

    # handle success
    if res.status_code == 200:
        return {
            'state': 'Success',
            'value': data['result']
        }

    # handle error
    else:
        return {
            'state': 'Error',
            'value': data['error']
        }



###########################################################################################################################################

###########################################################################################################################################
# Helper functions for cleaning order data


description_translate = {
    '"Please Enter Your Car Make/Model/Year so we can provide the correct Spigot Rings (if needed). We won\'t check wheel fitment - so if you\'re unsure on sizes just get in touch!":':'Provided Car:',
    'Step 1 - Start by choosing your PCD:':'PCD:',
    'Step 2 - Choose your Wheel Diameter:':'Wheel Diameter:',
    'Step 3 - Choose your Wheel Width:':'Wheel Width:',
    'Step 4 - What offset do you want?:':'Offset:',
    'Step 5 - What disk type do you want?:':'Disk Type:',
    'Step 5a - What brake setup are you running?:':'Brake Setup:',
    'Step 6 - Choose your Centre Colour:':'Centre Colour:',
    'Step 7 - choose your Lip Colour:':'Lip Colour:',
    'Step 8 - Choose Your Assembly Bolt Colour:':'Assembly Bolt Colour:',
    'WORK WHEEL SHIPPING METHOD:':'Work Wheel Shipping Method:'
}


def parse_product_description(description):
    product_options = []
    if description:
        # first replace all newlines with a custom separator, then split by that separator
        description = re.sub(r'\n+', '\n', description).replace('\n', '~DW~')
        description = description.split('~DW~')
        
        # loop over the desc pieces and find the data we want
        for piece in description:
            if 'Option Price' in piece: # should always be present
                # extract the data we want and clean it up before adding to the product options
                piece = piece.split('Option Price')[0].strip(' -')
                for find, repl in description_translate.items():
                    piece = piece.replace(find, repl)
                product_options.append(piece)
    return product_options





def get_eircode(postcode):
    """
    Returns the Irish county for a given postcode
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    # get session key for eircode website
    url = "https://api-finder.eircode.ie/Latest/findergetidentity"
    res = requests.get(url, headers=headers)
    key = res.json().get('key', '')

    # send post code to the eircode website
    if key:
        payload = {
            "key": key,
            "address": postcode,
            "language": "en",
            "geographicAddress": "true",
            "clientVersion": "388603cc"
        }
        url = "https://api-finder.eircode.ie/Latest/finderfindaddress"
        response = requests.get(url, payload, headers=headers)

        # try to get the postal address from the response
        try:
            postal = response.json()["postalAddress"]
            county = str(postal[-1]).upper().replace("CO. ", "")
            county = re.sub(r'\d+', '', county).strip()
            return {'state':'Success', 'value':county}

        # bad request error (key invalid or got blocked) are caught with this
        except Exception:
            return {'state':'Error', 'value':'eircode failed'}


def get_statecode(country, post_code):
    """
    Returns the USA/Canada state code for a given post code
    """
    nomi = Nominatim(country)
    result = nomi.query_postal_code(post_code)
    state_code = str(result["state_code"])
    if state_code != "nan":
        return {'state':'Success', 'value':state_code}
    else:
        return {'state':'Error', 'value':'pgeocode failed'}


###########################################################################################################################################
# Function for cleaning order data


def clean_data(data):
    # query db with country code, if not in then log this and let user know
    country_data = Countries.query.filter(Countries.country_name == data['shipping_country']).first()
    if country_data is not None: # match
        data['shipping_country_id'] = country_data.country_code # update shipping country code
        data['etd_required'] = 'on' if country_data.etd_required else 'off' # set on/off based on bool value of etd_required
        data['sat_indicator'] = 'Yes' if country_data.sat_indicator else '' # set on/off based on bool value of etd_required
    else: # no match
        data['etd_required'] = 'off'
        data['sat_indicator'] = ''
        update_log.create_log_line('results', f"`{data['shipping_country']}` is missing from `Countries` database.")




    # TRADER
    """
    If trader:
        do stuff
    Else:
        do other stuff
    """




    """
    also need to do the bad char replacer here
    eg U with umlaut goes to U
    BUT if replacements in 1 line >= 4 then we return that this is invalid
    """

    # strip any nonalphanumerical and non spaces out of the postcode
    data['shipping_postcode'] = re.sub(r'[^a-zA-Z0-9 ]', '', data['shipping_postcode'])




    # if the data is missing it's statecode then try to find it automatically based on the country
    # else just give it a random value because if it isnt explicitly being told to get a value then it isnt required
    if not data.get('shipping_statecode', ''):
        # ireland
        if data['shipping_country_id'] in ['IE']:
            result = get_eircode(data['shipping_postcode'])
            state_code = shipping_functions.get_state_code([result['value']])

        # usa/canada
        elif data['shipping_country_id'] in ['US', 'CA']:
            result = get_statecode(data['shipping_country_id'], data['shipping_postcode'])
            state_code = result['value']

        # all others
        else:
            result = {'state':'Success'}
            state_code = 'This will never see the light of day'

        # if the statecode was found then set it 
        if result['state'] == 'Success':
            data['shipping_statecode'] = state_code
        elif result['state'] == 'Error':
            data['shipping_statecode'] = 'manual'




    # loop over commerical invoice items and clean them up
    commercial_invoice = []
    lookup_commercial = {}
    for line in data['commercial_invoice_lines']:
        # need to extract the product options from the product description
        line['product_options'] = parse_product_description(line['line_description'])


        # set parcel insurance if it doesnt exist
        if line.get('parcel_insurance', '') == '':
            line['parcel_insurance'] = 0


        """
        This code here needs to be updated when we change the format we get our odoo orders back as, this should be used as a backup for compatibility with old orders.
        They will likely be fine though as the shipping items we want to set as 'False shippable' will also update for them too
        """
        # need to remove the shipping method from the commercial invoice
        if line['product_name'] != data['order_carrier_name']:
            commercial_invoice.append(line)


        # also need to update the lookup dict so later code can use it
        lookup_commercial[str(line['product_id'])] = line['product_sku']
    data['commercial_invoice_lines'] = commercial_invoice




    # loop over pack items and find the parent sku
    for line in data['order_items']:
        line['parent_sku'] = lookup_commercial[str(line['sale_product_id'])]

    return data


###########################################################################################################################################

###########################################################################################################################################
# Functions for sending response back to odoo


def send_ship_message(order_key, courier, tracking_no):
    # generate url
    url = join_url(api_base_url, 'dwapi', 'v1', 'orders', order_key, 'ship')

    # generate payload
    payload = {
        'tracking_ref': f'{courier}:{tracking_no}',
        'comment': 'test'
    }

    # get res and parse
    res = requests.post(url, headers=main_headers, json=payload).json()
    if res.get('error', '') != '':
        print(res)
    else:
        print(res)



# def send_pack_message(order_key, items):
#     # generate url
#     url = join_url(api_base_url, 'dwapi', 'v1', 'orders', order_key, 'pack')

#     # generate payload
#     picking_id = items.get("picking_id")
#     if len(items) <= 1:
#         body_data = {
#             "comment": f"IBAM2001 says:I (%whospacking%) have packed the following: {picking_id}",
#             "complete": True
#         }
#     else:
#         body_data = {
#             "comment": f"IBAM2001 says:I (%whospacking%) have packed the following: {picking_id}",
#             "complete": False,
#             "items": [
#                 {
#                     "product_id": key,
#                     "qty_shipped": value
#                 }
#                 for key, value in items.items() if key != "picking_id"
#             ]
#         }
#     print(body_data)
#     response = requests.post(url, headers=main_headers, json=body_data)
#     if response.status_code == 200:
#         return f"DONE: {response.json()}"
#     else:
#         return f"ERROR: {response}"