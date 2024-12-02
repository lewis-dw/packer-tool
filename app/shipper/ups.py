import os
import pathlib
from dotenv import load_dotenv
from app.shipper.shipping_functions import verify_line, get_shipping_date, get_country_code
import json
import requests
from requests.auth import HTTPBasicAuth

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))

# load env variables and set if using live or test
load_dotenv()
prefix = 'TEST_'
# prefix = ''

# get the url parts
auth_url = os.getenv(f'{prefix}UPS_OAUTH_URL')
label_url = os.getenv(f'{prefix}UPS_LABEL_URL')
quote_url = os.getenv(f'{prefix}UPS_QUOTE_URL')
void_url = os.getenv(f'{prefix}UPS_VOID_URL')

# get the credentials
_id = os.getenv(f'{prefix}UPS_ID')
secret = os.getenv(f'{prefix}UPS_SECRET')
account_id = os.getenv(f'{prefix}UPS_ACCOUNT_ID')


###########################################################################################################################################
# Helper functions


def get_auth():
    # if self.token and self.expires_at and time.time() + 60 < self.expires_at:
    #     return self.token
    payload = f"grant_type=client_credentials"
    headers = {'Content-Type': "application/x-www-form-urlencoded", "x-merchant-id": account_id}
    res = requests.post(auth_url, data=payload, headers=headers, auth=HTTPBasicAuth(_id, secret)).json()
    token = res["access_token"]
    return token





def format_items(data):
    # loop over the invoice lines to create each item
    all_items = []
    for invoice_line in data:
        # we need to only add commodity items for actual products not the shipping
        if verify_line(invoice_line['product_sku']):
            item_dict = {
                "PartNumber": invoice_line["product_sku"][:35],
                "Description": invoice_line["product_name"][:35],
                "Unit": {
                    "Value": invoice_line["unit_price"],
                    "Number": invoice_line["product_demand_qty"],
                    "UnitOfMeasurement": {
                        "Code": "EA"
                    }
                },
                "CommodityCode": invoice_line["commodity_code"],
                "OriginCountryCode": get_country_code(invoice_line["country_of_manufacture"]),
                "PackageWeight": {
                    "UnitOfMeasurement": "KGS",
                    "Weight": max(float(invoice_line["unit_weight"]), 1)
                },
            }
            all_items.append(item_dict)
    return all_items





def format_parcels(data, _extra=''):
    # loop over the invoice lines
    all_parcels = []
    for invoice_line in data:
        # we need to only create parcels for actual products not the shipping
        if verify_line(invoice_line['product_sku']):
            # loop over the number of parcels that a required for the invoice line
            parcels_extend = []
            for _ in range(int(float(invoice_line['product_demand_qty']))):
                # generate the parcel
                parcel_dict = {
                    "Description": "Products from Driftworks",
                    f"PackagingType{_extra}": {
                        "Code": "02",
                        "Description": ""
                    },
                    "Dimensions": {
                        "UnitOfMeasurement": {
                            "Description": "Dimensions",
                            "Code": "CM"
                        },
                        "Length": str(float(invoice_line['product_length'])),
                        "Width": str(float(invoice_line['product_width'])),
                        "Height": str(float(invoice_line['product_height']))
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Description": "Kilograms",
                            "Code": "KGS"
                        },
                        "Weight": str(float(invoice_line['unit_weight']))
                    }
                }

                # if there is insurance on the parcel add it in
                if invoice_line['parcel_insurance'] > 0.0:
                    parcel_dict["PackageServiceOptions"] = {
                        "DeclaredValue": {
                            "Type": {
                                "Code": "01"
                            },
                            "MonetaryValue": invoice_line['parcel_insurance'],
                            "CurrencyCode": "GBP"
                        }
                    }

                parcels_extend.append(parcel_dict)
            all_parcels.extend(parcels_extend)
    return all_parcels


###########################################################################################################################################
# Quoting


def create_quote_payload(data, parcels):
    payload = {
            "RateRequest": {
                "Request": {
                    "RequestOption": "Shop",
                    "TransactionReference": {
                        "CustomerContext": "CustomerContext"
                    }
                },
                "Shipment": {
                    "Shipper": {
                        "Name": "Driftworks",
                        "ShipperNumber": account_id,
                        "Address": {
                            "AddressLine": ["Driftworks", "Unit 7"],
                            "City": "Birmingham",
                            "PostalCode": "B112LQ",
                            "CountryCode": "GB"
                        }
                    },
                    "ShipTo": {
                        "Name": data['shipping_company'],
                        "Address": {
                            "AddressLine": [
                                data['shipping_street'],
                                data['shipping_street2'],
                                data['shipping_region']
                            ],
                            "City": data['shipping_locality'],
                            "PostalCode": data['shipping_postcode'],
                            "CountryCode": data['shipping_country_id']
                        }
                    },
                    "ShipFrom": {
                        "Name": "DRIFTWORKS LTD",
                        "Address": {
                            "AddressLine": ["Driftworks", "Unit 7"],
                            "City": "Birmingham",
                            "PostalCode": "B112LQ",
                            "CountryCode": "GB"
                        }
                    },
                    "NumOfPieces": len(parcels),
                    "Package": parcels,
                    "ShipmentRatingOptions": {
                        "NegotiatedRatesIndicator": {}
                    },
                    "ShipmentServiceOptions": {} # this has some weird SAT indicator mischief going into it but for now just ignore
                }
            }
        }

    # if the country code is in this list then it needs state_code which should be present due to earlier data verification
    if data['shipping_country_id'] in ['IE', 'US', 'CA']:
        payload["RateRequest"]["Shipment"]["ShipTo"]["Address"]["StateProvinceCode"] = data.get('shipping_statecode', '')
    return payload





def quote_order(data):
    # first check if our auth is valid still (or create a new one upon first run)
    token = get_auth()

    # generate parcels and items before creating payload
    parcels = format_parcels(data['commercial_invoice_lines'])

    # create the payload and header
    payload = create_quote_payload(data, parcels)
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
    }

    # quote the payload
    spayload = json.dumps(payload)
    res = requests.post(quote_url, data=spayload, headers=headers)

    # we want to dump the payload and response for debugging
    with open(os.path.join(debug_dir, 'quote', 'ups', 'payload.json'), 'w') as f:
        json.dump(payload, f, indent=4)
    with open(os.path.join(debug_dir, 'quote', 'ups', 'response.json'), 'w') as f:
        json.dump(res.json(), f, indent=4)

    # parse the result and return
    quotes = parse_response(res.json())
    return quotes





def parse_response(res):
    # check if we have errors
    if res.get('response', '') != '':
        errors = []
        for error in res['response']['errors']:
            errors.append({'courier': 'ups', 'error': f"{error['code']} - {error['message']}"})
        return {'state':'Error', 'value':errors}

    # no errors? lets go parsing!
    else:
        quotes = []
        for method in res["RateResponse"]["RatedShipment"]:
            quotes.append({
                'courier': 'ups',
                'method_name': method["Service"]["Code"],
                'cost': method["NegotiatedRateCharges"]["TotalCharge"]["MonetaryValue"]
            })
        return {'state':'Success', 'value':quotes}