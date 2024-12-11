import os
import pathlib
from dotenv import load_dotenv
from app.shipper.shipping_functions import get_shipping_date, get_country_code
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
                "Weight": invoice_line["unit_weight"]
            },
        }
        all_items.append(item_dict)
    return all_items





def format_parcels(data, _extra=''):
    # loop over the invoice lines
    all_parcels = []
    for invoice_line in data:
        # loop over the number of parcels that a required for the invoice line
        parcels_extend = []
        for _ in range(int(float(invoice_line['product_demand_qty']))):
            # generate the parcel
            parcel_dict = {
                "Description": "Products from Driftworks",
                f"Packaging{_extra}": {
                    "Code": "02",
                    "Description": ""
                },
                "Dimensions": {
                    "UnitOfMeasurement": {
                        "Description": "Centimetres",
                        "Code": "CM"
                    },
                    "Length": invoice_line['product_length'],
                    "Width": invoice_line['product_width'],
                    "Height": invoice_line['product_height']
                },
                "PackageWeight": {
                    "UnitOfMeasurement": {
                        "Description": "Kilograms",
                        "Code": "KGS"
                    },
                    "Weight": invoice_line['unit_weight']
                }
            }

            # if there is insurance on the parcel add it in
            if float(invoice_line['parcel_insurance']) > 0.0:
                parcel_dict["PackageServiceOptions"] = {
                    "DeclaredValue": {
                        # "Type": {
                        #     "Code": "01"
                        # },
                        "MonetaryValue": invoice_line['parcel_insurance'],
                        "CurrencyCode": "GBP"
                    }
                }

            parcels_extend.append(parcel_dict)
        all_parcels.extend(parcels_extend)
    return all_parcels





def clean_data(data):
    # regular data
    data['shipping_cost'] = round(float(data['shipping_cost']), 2)

    # clean commercial invoice lines
    for c, invoice_line in enumerate(data['commercial_invoice_lines']):
        # product dimensions
        data['commercial_invoice_lines'][c]['product_height'] = str(round(float(invoice_line['product_height']), 2))
        data['commercial_invoice_lines'][c]['product_width'] = str(round(float(invoice_line['product_width']), 2))
        data['commercial_invoice_lines'][c]['product_length'] = str(round(float(invoice_line['product_length']), 2))
        data['commercial_invoice_lines'][c]['unit_weight'] = str(max(float(invoice_line["unit_weight"]), 1))

        # costs
        data['commercial_invoice_lines'][c]['parcel_insurance'] = str(round(float(invoice_line['parcel_insurance']), 2))

    # return the cleaned data
    return data





def send_payload(url, payload):
    # get auth token then init headers
    token = get_auth()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # send the payload and return
    return requests.post(url, json=payload, headers=headers)


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
    # clean the data
    c_data = clean_data(data)

    # generate parcels before creating payload
    parcels = format_parcels(c_data['commercial_invoice_lines'], 'Type')
    payload = create_quote_payload(c_data, parcels)

    # quote the order
    res = send_payload(quote_url, payload)

    # we want to dump the payload and response for debugging
    with open(os.path.join(debug_dir, 'quote', 'ups', 'payload.json'), 'w') as f:
        json.dump(payload, f, indent=4)
    with open(os.path.join(debug_dir, 'quote', 'ups', 'response.json'), 'w') as f:
        json.dump(res.json(), f, indent=4)

    # parse the result and return
    quotes = parse_quote_response(res.json())
    return quotes





def parse_quote_response(res):
    # check if we have errors
    if res.get('response', '') != '':
        errors = []
        for error in res['response']['errors']:
            errors.append({
                'courier': 'ups',
                'error': f"{error['code']} - {error['message']}"
            })
        return {'state':'Error', 'value':errors}

    # no errors? lets go parsing!
    else:
        quotes = []
        for method in res["RateResponse"]["RatedShipment"]:
            quotes.append({
                'courier': 'ups',
                'shipping_code': method["Service"]["Code"],
                'cost': method["NegotiatedRateCharges"]["TotalCharge"]["MonetaryValue"]
            })
        return {'state':'Success', 'value':quotes}


###########################################################################################################################################
# Shipping


def create_ship_payload(data, shipping_code, parcels, items):
    payload = {
        "ShipmentRequest": {
            "Shipment": {
                "Description": "Thanks for your order!",
                "ReferenceNumber": {
                    "Code": "IK",
                    "Value": data['order_name']
                },
                "Shipper": {
                    "Name": "Driftworks",
                    "AttentionName": "Logistics",
                    "CompanyDisplayableName": "DW",
                    "TaxIdentificationNumber": "GB862889662",
                    "Phone": {
                        "Number": "441217922000"
                    },
                    "ShipperNumber": account_id,
                    "EMailAddress": "logistics@driftworks.com",
                    "Address": {
                        "AddressLine": ["Driftworks", "Unit 7"],
                        "City": "Birmingham",
                        "PostalCode": "B112LQ",
                        "CountryCode": "GB"
                    }
                },
                "ShipTo": {
                    "Name": data['shipping_company'],
                    "AttentionName": data['shipping_name'],
                    "Phone": {
                        "Number": data['shipping_telephone'],
                    },
                    "EMailAddress": data['customer_email'],
                    "Address": {
                        "AddressLine": [
                            data['shipping_street'],
                            data['shipping_street2'],
                            data['shipping_region']
                        ],
                        "City": data['shipping_locality'],
                        "CountryCode": data['shipping_country_id'],
                        "PostalCode": data['shipping_postcode'],
                        "ResidentialAddressIndicator": {}
                    }
                },
                "ShipFrom": {
                    "Address": {
                        "AddressLine": "Driftworks, Unit 7",
                        "City": "Birmingham",
                        "CountryCode": "GB",
                        "PostalCode": "B112LQ"
                    },
                    "AttentionName": "Nick Biggerstaff",
                    "Name": "DRIFTWORKS LTD",
                    "EMailAddress": "logistics@driftworks.com",
                    "Phone": {
                        "Number": "441217922000"
                    }
                },
                "PaymentInformation": {
                    "ShipmentCharge": {
                        "Type": "01",
                        "BillShipper": {
                            "AccountNumber": account_id
                        }
                    }
                },
                "Service": {
                    "Code": shipping_code,
                    "Description": ""
                },
                "Package": parcels,
                "ShipmentServiceOptions": {
                    "DeliveryConfirmation": {
                        "DCISType": 1
                    }
                },
                "ShipmentRatingOptions": {
                    "NegotiatedRatesIndicator": {},
                    "UserLevelDiscountIndicator": {},
                    "RateChartIndicator": {}
                },
            },
            "LabelSpecification": {
                "LabelImageFormat": {
                    "Code": "ZPL",
                    "Description": "ZPL Label"
                },
                "HTTPUserAgent": "Mozilla/4.5",
                "LabelStockSize": {
                    "Height": "6",
                    "Width": "4"
                }
            }
        }
    }


    # # if saturday then add saturday indicator
    # if SHIPPING_DATA.shipping_service_code == "SAT":
    #     payload["ShipmentRequest"]["Shipment"]["ShipmentServiceOptions"]["SaturdayDeliveryIndicator"] = {}
    #     payload["ShipmentRequest"]["Shipment"]["Service"] = "11"


    # if not gb then add the invoice
    if data['shipping_country_id'] != "GB":
        payload["ShipmentRequest"]["Shipment"]["ShipmentServiceOptions"]["InternationalForms"] = {
            "AdditionalDocumentIndicator": {},
            "Contacts": {
                "SoldTo": {
                    "Name": data['shipping_name'],
                    "EMailAddress": data['customer_email'],
                    "Phone": {
                        "Number": data['shipping_telephone']
                    },
                    "Address": {
                        "AddressLine": [
                            data['shipping_street'],
                            data['shipping_street2'],
                            data['shipping_region']
                        ],
                        "City": data['shipping_locality'],
                        "CountryCode": data['shipping_country_id'],
                    }
                }
            },
            "FormType": "01",
            "InvoiceNumber": data['order_name'],
            "InvoiceDate": get_shipping_date('16:00', 1, r'%Y%m%d'),
            "TermsOfShipment": "DAP",
            "ReasonForExport": "Sale",
            "Comments": "Commercial invoice for items dispatched from Driftworks Ltd",
            "DeclarationStatement": "I declare all the information contained in this invoice to be true and correct.",
            "CurrencyCode": "GBP",
            "FreightCharges": {
                "MonetaryValue": data['shipping_cost']
            },
            "Product": items,
        }


    # if they have provided a tax eori then add it in and label them as a business consumer
    if data['billing_vat_id'] and 1==0:
        payload['ShipmentRequest']['Shipment']['GlobalTaxInformation'] = {
            "ShipperTypeValue": "01",
            "AgentTaxIdentificationNumber": {
                "TaxIdentificationNumber": {
                    "IdentificationNumber": data['billing_vat_id']
                    # "IDNumberEncryptionIndicator": "0"
                }
            }
        }


    # if the country code is in this list then it needs state_code which should be present due to earlier data verification
    if data['shipping_country_id'] in ['IE', 'US', 'CA']:
        payload["ShipmentRequest"]["Shipment"]["ShipTo"]["Address"]["StateProvinceCode"] = data.get('shipping_statecode', '')
        payload["ShipmentRequest"]["Shipment"]["ShipmentServiceOptions"]["InternationalForms"]["Contacts"]["SoldTo"]["Address"]["StateProvinceCode"] = data.get('shipping_statecode', '')
    return payload





def ship_order(data, shipping_code):
    # clean the data
    c_data = clean_data(data)

    # generate parcels and items before creating payload
    items = format_items(c_data['commercial_invoice_lines'])
    parcels = format_parcels(c_data['commercial_invoice_lines'])
    payload = create_ship_payload(c_data, shipping_code, parcels, items)

    # ship the order
    res = send_payload(label_url, payload)

    # we want to dump the payload and response for debugging
    with open(os.path.join(debug_dir, 'ship', 'ups', 'payload.json'), 'w') as f:
        json.dump(payload, f, indent=4)
    with open(os.path.join(debug_dir, 'ship', 'ups', 'response.json'), 'w') as f:
        json.dump(res.json(), f, indent=4)

    # parse the result and return
    labels = parse_ship_response(res.json())
    return labels





def parse_ship_response(res):
    print(res)
    return {'state':'Error', 'value':'temp'}