import os
import pathlib
from dotenv import load_dotenv
from app.shipper.shipping_functions import verify_line, get_shipping_date, get_country_code
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
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    res = requests.post(auth_url, data=payload, headers=headers).json()
    token = res["access_token"]
    return token





def format_items(data):
    # loop over the invoice lines to create each item
    all_items = []
    for invoice_line in data:
        # we need to only add commodity items for actual products not the shipping
        if verify_line(invoice_line['product_sku']):
            item_dict = {
                "name": invoice_line["product_sku"][:35],
                "description": invoice_line["product_name"][:35],
                "countryOfManufacture": get_country_code(invoice_line["country_of_manufacture"]),
                "quantity": int(float(invoice_line["product_demand_qty"])),
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
        if verify_line(invoice_line['product_sku']):
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

                # if there is insurance on the parcel add it in
                if float(invoice_line['parcel_insurance']) > 0.0:
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


def create_quote_payload(data, items, parcels):
    payload = {
        "requestedShipment": {
            "shipper": {
                "address": {
                    "city": "Birmingham",
                    "postalCode": "B112LQ",
                    "countryCode": "GB",
                    "residential": False
                }
            },
            "recipient": {
                "address": {
                    "city": data['shipping_locality'],
                    "postalCode": data['shipping_postcode'],
                    "countryCode": data['shipping_country_id'],
                    "residential": True
                }
            },
            "shipDateStamp": get_shipping_date('12:00', 1, r'%Y-%m-%d'),
            "pickupType": "USE_SCHEDULED_PICKUP",
            "rateRequestType": [
                "ACCOUNT"
            ],
            "customsClearanceDetail": {
                "dutiesPayment": {
                    "paymentType": "SENDER",
                    "payor": {
                        "responsibleParty": None
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

    # if the country code is in this list then it needs state_code which should be present due to earlier data verification
    if data['shipping_country_id'] in ['IE', 'US', 'CA']:
        payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = data.get('shipping_statecode', '')
    return payload





def quote_order(data):
    # first check if our auth is valid still (or create a new one upon first run)
    token = get_auth()

    # generate parcels and items before creating payload
    items = format_items(data['commercial_invoice_lines'])
    parcels = format_parcels(data['commercial_invoice_lines'], data['order_name'])

    # create the payload and header
    payload = create_quote_payload(data, items, parcels)
    headers = {
        'Content-Type': "application/json",
        'X-locale': "en_US",
        'Authorization': f"Bearer {token}"
    }

    # quote the payload
    spayload = json.dumps(payload)
    res = requests.post(quote_url, data=spayload, headers=headers)

    # we want to dump the payload and response for debugging
    with open(os.path.join(debug_dir, 'quote', 'fedex', 'payload.json'), 'w') as f:
        json.dump(payload, f, indent=4)
    with open(os.path.join(debug_dir, 'quote', 'fedex', 'response.json'), 'w') as f:
        json.dump(res.json(), f, indent=4)

    # parse the result and return
    quotes = parse_response(res.json())
    return quotes





def parse_response(res):
    # check if we have errors
    if res.get('errors', '') != '':
        errors = []
        for error in res['errors']:
            errors.append({
                'courier': 'fedex',
                'error': f"{error['code']} - {error['message']}"
            })
        return {'state':'Error', 'value':errors}

    # no errors? lets go parsing!
    else:
        quotes = []
        for method in res['output']['rateReplyDetails']:
            quotes.append({
                'courier': 'fedex',
                'method_name': method['serviceType'],
                'cost': method["ratedShipmentDetails"][0]["totalNetCharge"]
            })
        return {'state':'Success', 'value':quotes}


###########################################################################################################################################
# Shipping


def create_ship_payload(data, shipping_code, size, items, parcels):
    payload = {
        "labelResponseOptions": "URL_ONLY",
        "requestedShipment": {
            "shipper": {
                "contact": {
                    "personName": "Nick Biggerstaff",
                    "phoneNumber": 441217922000,
                    "emailAddress": "logistics@driftworks.com",
                    "companyName": "Driftworks"
                },
                "address": {
                    "streetLines": [
                        "Driftworks, Unit 7"
                    ],
                    "city": "Birmingham",
                    "postalCode": "B112LQ",
                    "countryCode": "GB"
                }
            },
            "recipients": [
                {
                    "contact": {
                        "personName": data['shipping_name'],
                        "phoneNumber": data['customer_telephone'],
                        "companyName": data['shipping_company'],
                        "emailAddress": data['customer_email']
                    },
                    "address": {
                        "streetLines": [
                            data['shipping_street'],
                            data['shipping_street2'],
                            data['shipping_region']
                        ],
                        "city": data['shipping_locality'],
                        "postalCode": data['shipping_postcode'],
                        "countryCode": data['shipping_country_id']
                    }
                }
            ],
            "shipDatestamp": get_shipping_date('12:00', 1, r'%Y-%m-%d'),
            "serviceType": shipping_code,
            "packagingType": "YOUR_PACKAGING",
            "pickupType": "USE_SCHEDULED_PICKUP",
            "blockInsightVisibility": "false",
            "shippingChargesPayment": {
                "paymentType": "SENDER"
            },
            "labelSpecification": {
                "imageType": "ZPLII",
                "labelFormatType": "COMMON2D",
                "labelOrder": "SHIPPING_LABEL_FIRST",
                "labelStockType": size,
                "labelRotation": "UPSIDE_DOWN",
                "labelPrintingOrientation": "TOP_EDGE_OF_TEXT_FIRST",
                "customerSpecifiedDetail": {
                    "docTabContent": {
                        "docTabContentType": "BARCODED",
                        "barcoded": {
                            "symbology": "CODE39",
                            "specification": {
                                "zoneNumber": 1,
                                "header": "MAWB",
                                "dataField": "REPLY/SHIPMENT/MasterTrackingId/TrackingNumber",
                                "justification": "LEFT"
                            }
                        }
                    }
                }
            },
            "customsClearanceDetail": {
                "dutiesPayment": {
                    "paymentType": "RECIPIENT"
                },
                "commercialInvoice": {
                    "termsOfSale": "DDU",
                    "comments": ["Commercial invoice for items dispatched from Driftworks Ltd"],
                    "declarationStatement": "I declare all the information contained in this invoice to be true and correct.",
                    "freightCharge": {
                        "amount": round(float(data['shipping_cost']), 2),
                        "currency": "UKL"
                    }
                },
                "isDocumentOnly": "false",
                "commodities": items
            },
            "shippingDocumentSpecification": {
                "shippingDocumentTypes": [
                    "COMMERCIAL_INVOICE"
                ],
                "commercialInvoiceDetail": {
                    "customerImageUsages": [
                        {
                            "id": "IMAGE_1",
                            "type": "SIGNATURE",
                            "providedImageType": "SIGNATURE"
                        },
                        {
                            "id": "IMAGE_2",
                            "type": "LETTER_HEAD",
                            "providedImageType": "LETTER_HEAD"
                        }
                    ],
                    "documentFormat": {
                        "docType": "PDF",
                        "stockType": "PAPER_LETTER"
                    }
                }
            },
            "shipmentSpecialServices": {
                "etdDetail": {
                    "requestedDocumentTypes": [
                        "COMMERCIAL_INVOICE"
                    ]
                },
                "specialServiceTypes": [
                    "ELECTRONIC_TRADE_DOCUMENTS"
                ]
            },
            "requestedPackageLineItems": parcels
        },
        "accountNumber": {
            "value": account_id
        }
    }

    # if the country code is in this list then it needs state_code which should be present due to earlier data verification
    if data['shipping_country_id'] in ['IE', 'US', 'CA']:
        payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = data.get('shipping_statecode', '')
    return payload
