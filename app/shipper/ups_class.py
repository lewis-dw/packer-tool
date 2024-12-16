from app.shipper.courier import Courier
import os
import pathlib
import requests
from requests.auth import HTTPBasicAuth
import time
import base64
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


class UPS(Courier):
    def __init__(self):
        super().__init__(
            # credentials
            client_id = os.getenv(f'{prefix}UPS_ID'),
            client_secret = os.getenv(f'{prefix}UPS_SECRET'),
            account_id = os.getenv(f'{prefix}UPS_ACCOUNT_ID'),

            # urls
            auth_url = os.getenv(f'{prefix}UPS_OAUTH_URL'),
            quote_url = os.getenv(f'{prefix}UPS_QUOTE_URL'),
            ship_url = os.getenv(f'{prefix}UPS_SHIP_URL')
        )
        self.void_url = os.getenv(f'{prefix}UPS_VOID_URL')


###########################################################################################################################################
# Helper Functions


    def clean_data(self, data):
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


    def format_items(self, commercial_lines):
        # loop over the invoice lines to create each item
        all_items = []
        for invoice_line in commercial_lines:
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


    def format_parcels(self, parcels, _extra=''):
        # loop over the invoice lines
        all_parcels = []
        for parcel in parcels:
            # loop over the number of parcels that a required for the invoice line
            parcels_extend = []
            for _ in range(int(float(parcel['parcel_quantity']))):
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
                        "Length": str(parcel['parcel_length']),
                        "Width": str(parcel['parcel_width']),
                        "Height": str(parcel['parcel_height'])
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Description": "Kilograms",
                            "Code": "KGS"
                        },
                        "Weight": str(parcel['parcel_weight'])
                    }
                }

                # if there is insurance on the parcel add it in
                if float(parcel['parcel_insurance']) > 0.0:
                    parcel_dict["PackageServiceOptions"] = {
                        "DeclaredValue": {
                            # "Type": {
                            #     "Code": "01"
                            # },
                            "MonetaryValue": str(parcel['parcel_insurance']),
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
            headers={'Content-Type': "application/x-www-form-urlencoded", "x-merchant-id": self.account_id},
            data=f"grant_type=client_credentials",
            auth=HTTPBasicAuth(self.client_id, self.client_secret)
        )

        # on a fail just raise exception for now
        if res.status_code != 200:
            raise Exception(f"Auth failed: {res.text}")

        # on success save the new auth token
        self.token_expires_at = time.time() + int(res.json()["expires_in"])
        return res.json()["access_token"]


###########################################################################################################################################
# Quoting


    def create_quote_payload(self, data, parcels):
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
                        "ShipperNumber": self.account_id,
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
                    "ShipmentServiceOptions": {}
                }
            }
        }

        # if SAT indicator exists then add the indicator in
        if data.get('sat_indicator', '') != '':
            payload["RateRequest"]["Shipment"]["ShipmentServiceOptions"]["SaturdayDeliveryIndicator"] = {}

        # if the country code is in this list then it needs state_code which should be present due to earlier data verification
        if data['shipping_country_id'] in ['IE', 'US', 'CA']:
            payload["RateRequest"]["Shipment"]["ShipTo"]["Address"]["StateProvinceCode"] = data.get('shipping_statecode', '')
        return payload




    def quote_order(self, data):
        # clean the data
        c_data = self.clean_data(data)

        # generate parcels and items before creating payload
        parcels = self.format_parcels(c_data['parcels'], 'Type')
        payload = self.create_quote_payload(c_data, parcels)

        # quote the payload
        res = self.send_payload(self.quote_url, payload)

        # we want to dump the payload and response for debugging
        self.dump_json('quote', 'ups', 'payload.json', payload)
        self.dump_json('quote', 'ups', 'response.json', res)

        # parse the result and return
        quotes = self.parse_quote_response(res, data['sat_indicator'])
        return quotes




    def parse_quote_response(self, res, sat_indicator):
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
                    'cost': method["NegotiatedRateCharges"]["TotalCharge"]["MonetaryValue"],
                    'sat_indicator': sat_indicator
                })
            return {'state':'Success', 'value':quotes}


###########################################################################################################################################
# Shipping


    def create_ship_payload(self, data, shipping_code, parcels, items, sat_indicator):
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
                        "Phone": {
                            "Number": "441217922000"
                        },
                        "ShipperNumber": self.account_id,
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
                    "GlobalTaxInformation": {
                        "AgentTaxIdentificationNumber": {
                            "AgentRole": {
                                "IdentificationNumber": "GB862889662",
                                "IDNumberEncryptionIndicator": "0",
                                "IDNumberPurposeCode": "01"
                            }
                        }
                    },
                    "PaymentInformation": {
                        "ShipmentCharge": {
                            "Type": "01",
                            "BillShipper": {
                                "AccountNumber": self.account_id
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


        # if saturday then add saturday indicator
        if sat_indicator:
            payload["ShipmentRequest"]["Shipment"]["ShipmentServiceOptions"]["SaturdayDeliveryIndicator"] = {}


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




    def ship_order(self, data, shipping_code, sat_indicator):
        # clean the data
        c_data = self.clean_data(data)

        # generate parcels and items before creating payload
        items = self.format_items(c_data['commercial_invoice_lines'])
        parcels = self.format_parcels(c_data['parcels'])
        payload = self.create_ship_payload(c_data, shipping_code, parcels, items, sat_indicator)

        # ship the order
        res = self.send_payload(self.ship_url, payload)

        # we want to dump the payload and response for debugging
        self.dump_json('ship', 'ups', 'payload.json', payload)
        self.dump_json('ship', 'ups', 'response.json', res)

        # parse the result and return
        labels = self.parse_ship_response(res)
        return labels




    def parse_ship_response(self, res):
        # check if we have errors
        if res.get('response', '') != '': # this may break at some point because the json is clearly differently formatted for errors than successes
            errors = []                   # this leads me to believe that they may change it at some point but i can act quickly on it
            for error in res['response']['errors']:
                errors.append(f"{error['code']} - {error['message']}")
            errors = '||'.join(errors)
            return {'state':'Error', 'value':errors}



        # no errors? lets go parsing!
        else:
            # extract key values
            main_res = res['ShipmentResponse']['ShipmentResults']
            master_id = main_res['ShipmentIdentificationNumber']
            labels = main_res['PackageResults']


            # loop over the labels to extract the zpl data
            zpls = []
            for label_id, label in enumerate(labels):
                # create label name
                label_name = f'{master_id}_{label_id+1}'

                # grab graphic image and decode it to get zpl data
                graphic_image = label["ShippingLabel"]["GraphicImage"]
                label_data = base64.b64decode(graphic_image)
                zpl_data = label_data.decode('latin-1').replace('\n', '')

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
                    'labels': zpls
                }
            }


###########################################################################################################################################
# Voiding


    def void_order(self):
        raise NotImplementedError('Not yet implemented')