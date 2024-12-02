import requests
import json
import os
import pathlib
from dotenv import load_dotenv
import re


# load .env variables
load_dotenv()
api_base_url = os.getenv('API_BASE_URL')
main_headers = {"api_key": os.getenv('API_KEY')}


# vars
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))


###########################################################################################################################################
# Helper functions


def request_url(url, headers={}, data={}):
    """
    Simple function to hit a URL and return the result or the error code if it failed.
    Accepts headers and json data to pass in as well but they also have default values.
    """
    res = requests.get(url, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()
    else:
        return {'error':res.status_code}


def join_url(*url_parts):
    """
    Simple function to join all parts of the passed in url pieces and return
    This is because os.path.join doesnt work for URLs and i didnt want to muck about with other libraries when this is just as easy
    """
    url_parts = map(str, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url


###########################################################################################################################################
# stage 1 - getting all orders


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
    url = join_url(api_base_url, 'dwapi', 'orders')
    res = request_url(url, main_headers)
    with open(os.path.join(debug_dir, 'orders', 'all_orders_dump.json'), 'w') as f:
        json.dump(res, f, indent=4)

    # handle the response
    if res.get('error', 'no') == 'no':
        valid_orders = get_valid_orders(res['result'])
        if valid_orders:
            return 'Success', valid_orders
        else:
            return 'Fail', 'No valid orders'
    else:
        return 'Fail', res['error']


###########################################################################################################################################
# stage 2 - find the first valid order and return the values


def get_specific_order(order_id):
    # get the additional info about the order
    url = join_url(api_base_url, 'dwapi', 'order', order_id)
    res = request_url(url, main_headers)

    # if a success then save the result and dump the response to a json
    if res.get('error', 'no') == 'no':
        status = 'Success'
        data = res['result']

        with open(os.path.join(debug_dir, 'orders', 'order_dump.json'), 'w') as f:
            json.dump(res, f, indent=4)

    # if a fail then save the error
    else:
        status = 'Fail'
        data = res['error']

    # return the status of the request and the response
    return status, data


###########################################################################################################################################
# stage 3 - cleaning functions for the data


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








def clean_data(data):
    # loop over commerical invoice items and clean them up
    commercial_invoice = []
    for line in data['commercial_invoice_lines']:
        # need to extract the product options from the product description
        line['product_options'] = parse_product_description(line['line_description'])

        # need to remove the shipping method from the commercial invoice
        if line['product_name'] != data['order_carrier_name']:
            commercial_invoice.append(line)
    data['commercial_invoice_lines'] = commercial_invoice

    return data