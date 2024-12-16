from app.shipper.courier import Courier
import os
import pathlib
import requests
import time
from dotenv import load_dotenv
from app.shipper.shipping_functions import get_shipping_date, download_with_retries, get_country_code
from app.logger import update_log

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))

# load env variables and set if using live or test
load_dotenv()
prefix = 'TEST_'
# prefix = ''


class FedEx(Courier):
    def __init__(self):
        super().__init__(
            #credentials
            client_id = os.getenv(f'{prefix}FEDEX_ID'),
            client_secret = os.getenv(f'{prefix}FEDEX_SECRET'),
            account_id = os.getenv(f'{prefix}FEDEX_ACCOUNT_ID'),

            # urls
            auth_url = os.getenv(f'{prefix}FEDEX_OAUTH_URL'),
            quote_url = os.getenv(f'{prefix}FEDEX_QUOTE_URL'),
            ship_url = os.getenv(f'{prefix}FEDEX_SHIP_URL')
        )
        self.void_url = os.getenv(f'{prefix}FEDEX_VOID_URL')


###########################################################################################################################################
# Helper Functions


    def clean_data(self, data):
        # regular data
        data['shipping_cost'] = round(float(data['shipping_cost']), 2)

        # clean commercial invoice lines
        for c, invoice_line in enumerate(data['commercial_invoice_lines']):
            data['commercial_invoice_lines'][c]['product_demand_qty'] = round(float(invoice_line['product_demand_qty']))

            # product dimensions
            data['commercial_invoice_lines'][c]['product_height'] = max(float(invoice_line['product_height']), 1)
            data['commercial_invoice_lines'][c]['product_width'] = max(float(invoice_line['product_width']), 1)
            data['commercial_invoice_lines'][c]['product_length'] = max(float(invoice_line['product_length']), 1)
            data['commercial_invoice_lines'][c]['unit_weight'] = max(float(invoice_line["unit_weight"]), 1)

            # costs
            data['commercial_invoice_lines'][c]['unit_price'] = float(invoice_line["unit_price"])
            data['commercial_invoice_lines'][c]['parcel_insurance'] = float(invoice_line['parcel_insurance'])
        return data


    def format_items(self, commercial_lines):
        # loop over the invoice lines to create each item
        all_items = []
        for invoice_line in commercial_lines:
            item_dict = {
                "name": invoice_line["product_sku"][:35],
                "description": invoice_line["product_name"][:35],
                "countryOfManufacture": get_country_code(invoice_line["country_of_manufacture"]),
                "quantity": invoice_line['product_demand_qty'],
                "quantityUnits": "PCS",
                "unitPrice": {
                    "amount": invoice_line["unit_price"],
                    "currency": "UKL"
                },
                "customsValue": {
                    "amount": invoice_line['product_demand_qty'] * invoice_line["unit_price"],
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


    def format_parcels(self, commercial_lines, order_name):
        # loop over the invoice lines
        all_parcels = []
        for invoice_line in commercial_lines:
            # loop over the number of parcels that a required for the invoice line
            parcels_extend = []
            for _ in range(invoice_line['product_demand_qty']):
                # generate the parcel
                parcel_dict = {
                    "customerReferenceType": [
                        {
                            "customerReferenceType": "CUSTOMER_REFERENCE",
                            "value": order_name
                        }
                    ],
                    "groupPackageCount": 1,
                    "weight": {
                        "value": invoice_line['unit_weight'],
                        "units": "KG"
                    },
                    "dimensions": {
                        "length": invoice_line['product_length'],
                        "width": invoice_line['product_width'],
                        "height": invoice_line['product_height'],
                        "units": "CM"
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


    def send_payload(self, url, payload):
        # get auth
        self.token = self.update_auth()

        # send a request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        res = requests.post(url, headers=headers, json=payload)
        return res.json()


###########################################################################################################################################
# Authentication


    def update_auth(self):
        """Fetch and cache the authorization token."""
        # if a token exists and hasnt expired then we dont need a new one
        if self.token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.token

        # get auth token
        res = requests.post(
            self.auth_url,
            headers={'Content-Type': "application/x-www-form-urlencoded"},
            data=f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"
        )

        # on a fail just raise exception for now
        if res.status_code != 200:
            raise Exception(f"Auth failed: {res.text}")

        # on success save the new auth token
        self.token_expires_at = time.time() + int(res.json()["expires_in"])
        return res.json()["access_token"]


###########################################################################################################################################
# Quoting


    def create_quote_payload(self, data, items, parcels):
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
                "value": self.account_id
            }
        }

        # if the country code is in this list then it needs state_code which should be present due to earlier data verification
        if data['shipping_country_id'] in ['IE', 'US', 'CA']:
            payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = data.get('shipping_statecode', '')
        return payload




    def quote_order(self, data):
        # clean the data
        c_data = self.clean_data(data)

        # generate parcels and items before creating payload
        items = self.format_items(c_data['commercial_invoice_lines'])
        parcels = self.format_parcels(c_data['commercial_invoice_lines'], c_data['order_name'])
        payload = self.create_quote_payload(c_data, items, parcels)

        # quote the payload
        res = self.send_payload(self.quote_url, payload)

        # we want to dump the payload and response for debugging
        self.dump_json('quote', 'fedex', 'payload.json', payload)
        self.dump_json('quote', 'fedex', 'response.json', res)

        # parse the result and return
        quotes = self.parse_quote_response(res)
        return quotes




    def parse_quote_response(self, res):
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
                    'shipping_code': method['serviceType'],
                    'cost': method["ratedShipmentDetails"][0]["totalNetCharge"],
                    'sat_indicator': ''
                })
            return {'state':'Success', 'value':quotes}


###########################################################################################################################################
# Shipping


    def create_ship_payload(self, data, shipping_code, label_size, items, parcels):
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
                            "phoneNumber": data['shipping_telephone'],
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
                    "labelStockType": label_size,
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
                            "amount": data['shipping_cost'],
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
                "requestedPackageLineItems": parcels
            },
            "accountNumber": {
                "value": self.account_id
            }
        }

        # if the country code is in this list then it needs state_code which should be present due to earlier data verification
        if data['shipping_country_id'] in ['IE', 'US', 'CA']:
            payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = data.get('shipping_statecode', '')

        # if etd is required then add it in
        if data['etd_required'] == 'on':
            payload['requestedShipment']['shipmentSpecialServices'] = {
                "etdDetail": {
                    "requestedDocumentTypes": [
                        "COMMERCIAL_INVOICE"
                    ]
                },
                "specialServiceTypes": [
                    "ELECTRONIC_TRADE_DOCUMENTS"
                ]
            }
        return payload




    def ship_order(self, data, shipping_code, printer_size):
        # translate the label size
        size_translate = {
            '4x675':'STOCK_4X675_LEADING_DOC_TAB',
            '4x6':'STOCK_4X6'
        }

        # clean the data
        c_data = self.clean_data(data)

        # generate parcels and items before creating payload
        items = self.format_items(c_data['commercial_invoice_lines'])
        parcels = self.format_parcels(c_data['commercial_invoice_lines'], c_data['order_name'])
        label_size = size_translate.get(printer_size, 'STOCK_4X6')
        payload = self.create_ship_payload(c_data, shipping_code, label_size, items, parcels)

        # ship the order
        res = self.send_payload(self.ship_url, payload)

        # we want to dump the payload and response for debugging
        self.dump_json('ship', 'fedex', 'payload.json', payload)
        self.dump_json('ship', 'fedex', 'response.json', res)

        # parse the result and return
        res = self.parse_ship_response(res)
        return res




    def parse_ship_response(self, res):
        # check if we have errors
        if res.get('errors', '') != '':
            errors = []
            for error in res['errors']:
                errors.append(f"{error['code']} - {error['message']}")
            errors = '||'.join(errors)
            return {'state':'Error', 'value':errors}



        # no errors? lets go parsing!
        else:
            # extract key values
            main_res = res['output']['transactionShipments'][0]
            master_id = main_res['masterTrackingNumber']
            commerical_invoice_url = main_res['shipmentDocuments'][0]['url']
            labels = main_res['pieceResponses']


            # attempt to download the commericial invoice and return result
            res = download_with_retries(commerical_invoice_url, delay=1, max_retry=100)
            value = res['value']
            if res['state'] == 'Error':
                update_log.create_log_line('results', f'Commercial invoice download failed: {value}. Available at: {commerical_invoice_url}')
                pdf_data = None
            else:
                """Send the pdf to database"""
                pdf_data = res['value'].content


            # loop over the labels to extract the zpl data
            zpls = []
            for label in labels:
                # grab label name
                label_name = label['trackingNumber']

                # grab label url and download it to get zpl data
                label_data_url = label['packageDocuments'][0]['url']
                res = download_with_retries(label_data_url, delay=1, max_retry=100)
                value = res['value']
                if res['state'] == 'Error':
                    update_log.create_log_line('results', f'ZPL file {label_name} download failed: {value}. Available at: {label_data_url}')
                    zpl_data = None
                else:
                    zpl_data = value

                # append raw zpl data to the labels list
                zpls.append({
                    'label_name': label_name,
                    'label_data': zpl_data
                })


            # return the data
            return {
                'state': 'Success',
                'value': {
                    'master_id': master_id,
                    'labels': zpls,
                    'commercial_invoice': pdf_data
                }
            }


###########################################################################################################################################
# Voiding


    def void_order(self):
        raise NotImplementedError('Not yet implemented')