import requests
import json
import os
import pathlib
from dotenv import load_dotenv
import re
from pgeocode import Nominatim
from app.logger import update_log

# database
from app.models import Countries, StateCodes, ForeignCharacters, ProductOptions

# load .env variables
load_dotenv()
prefix = os.getenv('PREFIX')
api_base_url = os.getenv(f'{prefix}ODOO_API_BASE_URL')
main_headers = {"api_key": os.getenv(f'{prefix}ODOO_API_KEY')}


# debug output
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
    url_parts = map(lambda p: str(p).strip('/'), url_parts)
    url_parts = filter(None, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url


###########################################################################################################################################

###########################################################################################################################################
# Functions for getting all orders


def get_valid_orders(content):
    # loop over the content and check if the order wants to be completed
    valid_orders = []
    for order in content:
        has_pack = order.get('to_pack', None)

        # based on these conditions determine if the order is valid
        if has_pack:
            valid_orders.append(order)
    return valid_orders


def get_orders():
    """Request all current orders and return the first one that wants to be processed."""

    # build url and query it
    url = join_url(api_base_url, 'dwapi', 'v1', 'orders')
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
    url = join_url(api_base_url, 'dwapi', 'v1', 'order', order_id)
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




def us_commodity_code_check(code, name):
    commodity_code_ranges = [(73000000, 74000000), (84000000, 85000000), (87000000, 88000000), (90000000, 91000000)]
    for start, end in commodity_code_ranges:
        if start < int(code) < end:
            name = f"{name} (For Motorsport Use Only!)"
            break
    return name




def clean_string(s, foreign_translate):
    # init vars
    valid_chars = ''.join([
        '0123456789',
        'abcdefghijklmnopqrstuvwxyz',
        '/,.+- <>()'
    ])
    replacement_counter = 0
    rebuild_string = ''
    bad_chars = ''

    # loop over the value and if a bad character is found then try to translate it
    for char in s:
        # if the char is not a valid one then increment the counter
        if str(char).lower() not in valid_chars:
            replacement_counter+=1
            bad_chars+=char

        # see if we have a translation for it
        char = foreign_translate.get(char, char)

        # rebuild the string piece by piece
        rebuild_string+=char

    # return the cleaned string and the number of replacements made
    return rebuild_string, replacement_counter, bad_chars




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
                description_translate = ProductOptions.get_replacers()
                for find, repl in description_translate:
                    piece = piece.replace(find, repl)
                product_options.append(piece)
    return product_options


def filter_valid_commercial(data):
    # lewis - also change data to be vvvvvvvv so i only need to pass that list in
    commercial_lines = data['commercial_invoice_lines']
    valid_lines = []
    for line in commercial_lines:
        if line['product_name'] != data['order_carrier_name']: # lewis <- this needs to be changed post odoo api update to filter the shipping/discount crap
            valid_lines.append(line)
        else:
            continue
    return valid_lines


def split_commercial_invoice(commercial_lines, pack_items):
    # create a set of each unique sale product id from the pack items
    sale_product_ids = {str(item["sale_product_id"]) for item in pack_items}

    # separate commercial_invoice_lines into two lists
    wanted = []
    unwanted = []
    for line in commercial_lines:
        if str(line["product_id"]) in sale_product_ids:
            wanted.append(line)
        else:
            unwanted.append(line)
    return wanted, unwanted


###########################################################################################################################################
# Function for cleaning order data


def clean_data(data):
    # this var tracks if there is a need for user to manually select something
    user_intervention = False


    """ Data cleaning """
    # clean every single item
    foreign_translate = ForeignCharacters.get_replacers()
    for key, value in data.items():
        # if the value is a string then proceed to clean it
        if isinstance(value, str):
            # clean the string
            data[key], r_count, bad_chars = clean_string(value, foreign_translate)

            # if the number of replacements was 4 or more then abort!
            if r_count >= 4:
                return {'state': 'Error', 'value': f'Too many bad characters in `{key}`:{bad_chars}'}

        # else if the value is a list then we still want to check it but it requires an extra step
        elif isinstance(value, list):
            """Lewis"""


    # clean the html from the customer and internal comments
    for field_name in ['picking_internal_note', 'picking_customer_note']:
        note = re.sub(r'<.*?>', ' ', data[field_name])
        data[field_name] = re.sub(r' +', ' ', note).strip()

    # strip any nonalphanumerical and non spaces out of the postcode
    if data['shipping_postcode']:
        data['shipping_postcode'] = re.sub(r'[^a-zA-Z0-9 ]', '', data['shipping_postcode'])

    # clean customer name
    data['shipping_name'] = re.sub(' +', ' ', data['shipping_name']).strip()



    """ Country Shipping Details """
    # query db with country code, if not in then log this and let user know
    country_data = Countries.get_country_data(data['shipping_country'])
    if country_data is not None: # match
        data['shipping_country_id'] = country_data.country_code # update shipping country code
        data['etd_required'] = 'on' if country_data.etd_required else 'off' # set on/off based on bool value of etd_required
        data['sat_indicator'] = 'Yes' if country_data.sat_indicator else '' # set on/off based on bool value of etd_required
    else: # no match
        data['etd_required'] = 'off'
        data['sat_indicator'] = ''
        update_log.create_log_line('results', f"`{data['shipping_country']}` is missing from `Countries` database.")



    """ General Shipping Details """
    # translate customer type to friendly version
    customer_translate = {
        'Public Pricelist': 'General Customer',
        'Trade1': 'Trader'
    }
    data['customer_pricelist'] = customer_translate.get(data['customer_pricelist'], data['customer_pricelist'])

    # make shipping company the same as the shiping name if it is in the bad vals list
    bad_vals = ['n/a', 'no', 'none', 'false', '']
    if str(data['shipping_company']).strip().lower() in bad_vals:
        data['shipping_company'] = data['shipping_name']



    """ Shipping Statecode """
    # if the data is missing it's statecode then try to find it automatically based on the country
    # else just give it a random value because if it isnt explicitly being told to get a value then it isnt required
    if not data.get('shipping_statecode', ''):
        # ireland
        if data['shipping_country_id'] in ['IE']:
            result = get_eircode(data['shipping_postcode'])
            state_code = StateCodes.get_state_code([result['value']])

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
            user_intervention = True
            data['shipping_statecode'] = 'manual'



    """ Commercial Invoice """
    # first i need only the valid commercial invoice lines and i also want to extract the correct items to pack as a separate key
    # commercial_invoice_lines = filter_valid_commercial(data['commercial_invoice_lines']) # uncomment when i get what i want form odoo api update
    commercial_invoice_lines = filter_valid_commercial(data)
    data['pack_items'] = data['order_items']['pack']

    # then i want to split the commercial invoice items
    wanted_commercial_invoice, unwanted_commercial_invoice = split_commercial_invoice(commercial_invoice_lines, data['pack_items'])


    # loop over commerical invoice items and clean them up
    needs_a_hand = []
    lookup_commercial = {}
    for line in wanted_commercial_invoice:
        """
        This code here needs to be updated when we change the format we get our odoo orders back as, this should be used as a backup for compatibility with old orders.
        They will likely be fine though as the shipping items we want to set as 'False shippable' will also update for them too
        """
        # need to extract the product options from the product description
        line['product_options'] = parse_product_description(line['line_description'])


        # check if commodity code exists
        if line.get('commodity_code', ''):
            # if we are shipping to the USA and the product has a certain commodity code then we need to add a legal string to each commercial invoice item
            if data['shipping_country_id'] == 'US':
                line['product_name'] = us_commodity_code_check(line['commodity_code'], line['product_name'])
        else:
            user_intervention = True
            line['commodity_code'] = ''
            needs_a_hand.append({
                'product_name': line['product_name'],
                'product_sku': line['product_sku']
            })


        # set parcel insurance if it doesnt exist
        if line.get('parcel_insurance', '') == '':
            line['parcel_insurance'] = 0


        # calculate the number of items actually wanted
        line['qty_wanted'] = line['product_demand_qty'] - line['product_delivered_qty'] # lewis
        " This is incomplete i havent worked out what i want to do with qty wanted "


        # also need to update the lookup dict so later code can use it
        lookup_commercial[str(line['product_id'])] = {
            'sku': line['product_sku'],
            'demand_qty': line['product_demand_qty'] # lewis - remember if i want this to be qty wanted etc post odoo update
        }

    data['commercial_invoice_lines'] = wanted_commercial_invoice # re-assign the commercial invoice key to the cleaned and valid lines
    data['unwanted_commercial_invoice_lines'] = unwanted_commercial_invoice # still store the unwanted ones because why not, you cant stop me
    data['needs_a_hand'] = needs_a_hand # add in the commercial invoice items that need a hand from the user


    """ Pack Items """
    # loop over pack items
    for item in data['pack_items']:
        # find the parent sku
        parent_product = lookup_commercial[str(item['sale_product_id'])]
        item['parent_sku'] = parent_product['sku']

        # parse product options
        item['product_options'] = parse_product_description(item['line_description'])

        # calculate the n of items per 1 parent product
        item['per_one_parent'] = item['product_demand_qty'] / parent_product['demand_qty']


    # return a successful clean
    return {'state': 'Success', 'value': [data, user_intervention]}


###########################################################################################################################################

###########################################################################################################################################
# Function for returning pack response back to Odoo


def create_message(invoice_lines):
    """Helper function to construct a message for what items are packed"""
    done_items = []
    for line_dict in invoice_lines:
        qty = int(float(line_dict['product_demand_qty']))
        if qty > 0:
            done_items.append(f"{line_dict['product_sku']} (x{qty})")
    return ' | '.join(done_items)


def count_items_done(invoice_lines):
    """Helper function to count up all items done and return"""
    count = 0
    for line_dict in invoice_lines:
        count += float(line_dict['product_demand_qty'])
    return int(count)


def parse_items(items):
    """Helper function to get only the values we want for items"""
    new_items = []
    for item_dict in items:
        qty = int(float(item_dict['product_demand_qty']))
        if qty > 0:
            new_items.append({
                "product_id": item_dict['product_id'],
                "qty_done": int(float(item_dict['product_demand_qty']))
            })
    return new_items


def send_pack_message(shipper, data, tracking_number):
    # generate url
    url = join_url(api_base_url, 'dwapi', 'v1', 'order', data['order_name'], 'pack')

    # extract values
    pack_id = data['picking_names']
    done_items = create_message(data['commercial_invoice_lines'])
    n_kits_done = count_items_done(data['commercial_invoice_lines'])
    pack_items = parse_items(data['pack_items'])

    # generate payload
    if n_kits_done == 0:
        payload = {
            'comment': f'IBAM2001: {shipper} has packed none of the {pack_id}',
            'complete': False
        }
    else:
        payload = {
            'comment': f'IBAM2001: {shipper} has packed {n_kits_done} of {pack_id}<br>Items: {done_items}<br>Tracking Number: {tracking_number}',
            'complete': False,
            'items': pack_items
        }

    response = requests.post(url, headers=main_headers, json=payload)
    print(response.text)
    #{"jsonrpc": "2.0", "id": null, "result": {"success": "Picking stage marked done"}}




def send_ship_message(order_name, courier, tracking_no):
    # generate url
    url = join_url(api_base_url, 'dwapi', 'v1', 'order', order_name, 'ship')
    print(url)

    # generate payload
    payload = {
        'tracking_ref': f'{courier}: {tracking_no}',
        'comment': f'This has been shipped.', # lewis
        'complete': True
    }

    # get res and parse
    res = requests.post(url, headers=main_headers, json=payload)
    print(res)
    print(res.json())
    # if res.get('error', '') != '':
    #     print(res)
    # else:
    #     print(res)
