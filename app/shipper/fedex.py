import os
import pathlib
from dotenv import load_dotenv
from app.shipper.shipping_functions import verify_line, get_shipping_date, find_statecode
import json
import requests

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))

# load env variables and set if using live or test
load_dotenv()
prefix = 'TEST_'
# prefix = ''

# get the url parts
auth_url = os.getenv(f'{prefix}FEDEX_OAUTH_URL')
label_url = os.getenv(f'{prefix}FEDEX_LABEL_URL')
quote_url = os.getenv(f'{prefix}FEDEX_QUOTE_URL')
void_url = os.getenv(f'{prefix}FEDEX_VOID_URL')

# get the credentials
_id = os.getenv(f'{prefix}FEDEX_ID')
secret = os.getenv(f'{prefix}FEDEX_SECRET')
account_id = os.getenv(f'{prefix}FEDEX_ACCOUNT_ID')


###########################################################################################################################################
# Helper functions


def get_auth():
    # if self.token and self.expires_at and time.time() + 60 < self.expires_at:
    #     return self.token
    payload = f"grant_type=client_credentials&client_id={_id}&client_secret={secret}"
    header = {'Content-Type': "application/x-www-form-urlencoded"}
    response = requests.post(auth_url, data=payload, headers=header)
    token = response.json()["access_token"]
    return token





def format_items(data):
    # loop over the invoice lines to create each item
    all_items = []
    for invoice_line in data:
        # we need to only add commodity items for actual products not the shipping
        if verify_line(invoice_line['product_name']):
            item_dict = {
                "name": invoice_line["product_sku"][:35],
                "description": invoice_line["product_name"][:35],
                "countryOfManufacture": invoice_line["country_of_manufacture"],
                "quantity": invoice_line["product_demand_qty"],
                "quantityUnits": "PCS",
                "unitPrice": {
                    "amount": invoice_line["unit_price"],
                    "currency": "UKL"
                },
                "customsValue": {
                    "amount": float(invoice_line["product_demand_qty"]) * float(invoice_line["unit_price"]),
                    "currency": "UKL"
                },
                "weight": {
                    "units": "KG",
                    "value": invoice_line["unit_weight"]
                },
                "harmonizedCode": invoice_line["commodity_code"]
            }
            all_items.append(item_dict)
    return all_items





def format_parcels(data, order_id):
    # loop over the invoice lines
    all_parcels = []
    for invoice_line in data:
        # we need to only create parcels for actual products not the shipping
        if verify_line(invoice_line['product_name']):
            # loop over the number of parcels that a required for the invoice line
            parcels_extend = []
            for _ in range(int(float(invoice_line['product_demand_qty']))):
                # generate the parcel
                parcel_dict = {
                    "customerReferenceType": [
                        {
                            "customerReferenceType": "CUSTOMER_REFERENCE",
                            "value": order_id
                        }
                    ],
                    "groupPackageCount": 1,
                    "weight": {
                        "value": max(float(invoice_line['unit_weight']), 1),
                        "units": "KG"
                    },
                    "dimensions": {
                        "length": max(float(invoice_line['product_length']), 1),
                        "width": max(float(invoice_line['product_width']), 1),
                        "height": max(float(invoice_line['product_height']), 1),
                        "units": "CM"
                    }
                }
                parcels_extend.append(parcel_dict)
            all_parcels.extend(parcels_extend)
    return all_parcels


###########################################################################################################################################
# Quoting Stage 1 - Load data into correct format


def create_payload(data, items, parcels):
    payload = {
        "requestedShipment": {
            "shipper": {
                "address": {
                    "city": "Birmingham",
                    "postalCode": "B112LQ",
                    "countryCode": "GB",
                    "residential": "false"
                }
            },
            "recipient": {
                "address": {
                    "city": data['shipping_locality'],
                    "postalCode": data['shipping_postcode'],
                    "countryCode": data['shipping_country_id'],
                    "residential": "true"
                }
            },
            "shipDateStamp": get_shipping_date('16:00', 1, r'%Y-%m-%d'),
            "pickupType": "USE_SCHEDULED_PICKUP",
            "rateRequestType": [
                "ACCOUNT"
            ],
            "customsClearanceDetail": {
                "dutiesPayment": {
                    "paymentType": "SENDER",
                    "payor": {
                        "responsibleParty": "null"
                    }
                },
                "commodities": items
            },
            "totalPackageCount": len(parcels),
            "requestedPackageLineItems": parcels
        },
        "accountNumber": {
            "value": account_id
        }
    }

    if data['shipping_country_id'] in ['IE', 'US', 'CA']:
        # needs 'stateOrProvinceCode' in recipient address (this should exist due to earlier data verification)
        payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = data.get('shipping_statecode', '')
    return payload, data




def quote_order(data):
    # first check if our auth is valid still (or create a new one upon first run)
    token = get_auth()

    # generate parcels and items before creating payload
    items = format_items(data['commercial_invoice_lines'])
    parcels = format_parcels(data['commercial_invoice_lines'], data['order_name'])

    # create the payload and header
    payload, data = create_payload(data, items, parcels)
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
    }

    # quote the payload
    # payload = json.dumps(payload).replace('"null"', 'null').replace('"true"', 'true').replace('"false"', 'false')
    res = requests.post(quote_url, data=payload, headers=headers)

    # we want to dump the payload and response for debugging
    with open(os.path.join(debug_dir, 'quote', 'fedex', 'payload.json'), 'w') as f:
        json.dump(payload, f, indent=4)
    with open(os.path.join(debug_dir, 'quote', 'fedex', 'response.json'), 'w') as f:
        json.dump(res.json(), f, indent=4)

    return res, data
