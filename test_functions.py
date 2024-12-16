from app.shipper import fedex_class, royal_mail_class


fedex = fedex_class.FedEx()


url = "https://apis-sandbox.fedex.com/rate/v1/rates/quotes"

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
                "city": "Exmouth",
                "postalCode": "EX8 4EE",
                "countryCode": "GB",
                "residential": False
            }
        },
        "shipDateStamp": "2024-12-16",
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
            "commodities": [
                {
                    "name": "DW-S-LIGHT-NS1497-02-3-J-00",
                    "description": "Nissan S14 200sx/Silvia/Kouki (96-9",
                    "countryOfManufacture": "TW",
                    "quantity": 1,
                    "quantityUnits": "PCS",
                    "unitPrice": {
                        "amount": 54.16,
                        "currency": "UKL"
                    },
                    "customsValue": {
                        "amount": 54.16,
                        "currency": "UKL"
                    },
                    "weight": {
                        "units": "KG",
                        "value": 1
                    },
                    "harmonizedCode": "85129090"
                },
                {
                    "name": "DW-S-LIGHT-SP3-NI2013SCH",
                    "description": "Nissan S14 200sx/Silvia/Kouki (93-9",
                    "countryOfManufacture": "TW",
                    "quantity": 1,
                    "quantityUnits": "PCS",
                    "unitPrice": {
                        "amount": 287.49,
                        "currency": "UKL"
                    },
                    "customsValue": {
                        "amount": 287.49,
                        "currency": "UKL"
                    },
                    "weight": {
                        "units": "KG",
                        "value": 1.8
                    },
                    "harmonizedCode": "85129090"
                },
                {
                    "name": "WF-S-SPARE-WF1142_500A",
                    "description": "Wisefab Spare - Nissan S14 Rear Sus",
                    "countryOfManufacture": "EE",
                    "quantity": 1,
                    "quantityUnits": "PCS",
                    "unitPrice": {
                        "amount": 178.88,
                        "currency": "UKL"
                    },
                    "customsValue": {
                        "amount": 178.88,
                        "currency": "UKL"
                    },
                    "weight": {
                        "units": "KG",
                        "value": 5.0
                    },
                    "harmonizedCode": "87085091"
                }
            ]
        },
        "totalPackageCount": 3,
        "requestedPackageLineItems": [
            {
                "customerReferenceType": [
                    {
                        "customerReferenceType": "CUSTOMER_REFERENCE",
                        "value": "S125951"
                    }
                ],
                "groupPackageCount": 1,
                "weight": {
                    "value": 1,
                    "units": "KG"
                },
                "dimensions": {
                    "length": 25.0,
                    "width": 24.0,
                    "height": 13.0,
                    "units": "CM"
                }
            },
            {
                "customerReferenceType": [
                    {
                        "customerReferenceType": "CUSTOMER_REFERENCE",
                        "value": "S125951"
                    }
                ],
                "groupPackageCount": 1,
                "weight": {
                    "value": 1.8,
                    "units": "KG"
                },
                "dimensions": {
                    "length": 39.0,
                    "width": 23.0,
                    "height": 18.0,
                    "units": "CM"
                }
            },
            {
                "customerReferenceType": [
                    {
                        "customerReferenceType": "CUSTOMER_REFERENCE",
                        "value": "S125951"
                    }
                ],
                "groupPackageCount": 1,
                "weight": {
                    "value": 5.0,
                    "units": "KG"
                },
                "dimensions": {
                    "length": 20.0,
                    "width": 20.0,
                    "height": 20.0,
                    "units": "CM"
                }
            }
        ]
    },
    "accountNumber": {
        "value": "802255209"
    }
}
res = fedex.send_payload(url, payload)

print(res)