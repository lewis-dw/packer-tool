import requests
import json
import os
import pathlib
from dotenv import load_dotenv


# load .env variables
load_dotenv()
api_base_url = os.getenv('API_BASE_URL')
main_headers = {"api_key": os.getenv('API_KEY')}


# vars
cur_dir = pathlib.Path(__file__).parent


###########################################################################################################################################
# used functions


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
    with open(os.path.join(cur_dir, 'all_orders_dump.json'), 'w') as f:
        json.dump(res, f, indent=4)

    # handle the response
    if res.get('error', 'no') == 'no':
        valid_orders = get_valid_orders(res['result'])
        print(f'{len(valid_orders)} orders waiting to be processed.')
        return 'Success', valid_orders
    else:
        return 'Fail', res['error']


###########################################################################################################################################
# stage 2 - find the first valid order and return the values



def get_specific_order(order_id):
    # here we can query a table containing the last updated valid orders with a column for if they are being worked on
    # then merge these 2 results together and use that
    status = 'Fail'
    data = 'Error'

    # get the additional info about the order
    url = join_url(api_base_url, 'dwapi', 'order', order_id)
    res = request_url(url, main_headers)
    if res.get('error', 'no') == 'no':
        status = 'Success'
        data = res['result']

        with open(os.path.join(cur_dir, 'order_dump.json'), 'w') as f:
            json.dump(res, f, indent=4)

    # if no orders then return a fail
    return status, data