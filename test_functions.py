from app.shipper import fedex_class, royal_mail_class, ups_class


fedex = fedex_class.FedEx()
ups = ups_class.UPS()


url = "https://wwwcie.ups.com/api/shipments/v2403/ship"

payload = {
    "ShipmentRequest": {
        "Shipment": {
            "Description": "Thanks for your order!",
            "ReferenceNumber": {
                "Code": "IK",
                "Value": "S125951"
            },
            "Shipper": {
                "Name": "Driftworks",
                "AttentionName": "Logistics",
                "CompanyDisplayableName": "DW",
                "Phone": {
                    "Number": "441217922000"
                },
                "ShipperNumber": "43X322",
                "EMailAddress": "logistics@driftworks.com",
                "Address": {
                    "AddressLine": [
                        "Driftworks",
                        "Unit 7"
                    ],
                    "City": "Birmingham",
                    "PostalCode": "B112LQ",
                    "CountryCode": "GB"
                }
            },
            "ShipTo": {
                "Name": "Alex Williams",
                "AttentionName": "Alex Williams",
                "Phone": {
                    "Number": "+447821749482"
                },
                "EMailAddress": "alexwilliams1711@gmail.com",
                "Address": {
                    "AddressLine": [
                        "Uplands",
                        "Bassetts Gardens",
                        ""
                    ],
                    "City": "Exmouth",
                    "CountryCode": "GB",
                    "PostalCode": "EX8 4EE",
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
                        "IDNumberPurposeCode": "01",
                        "IDNumberSubTypeCode": "0"
                    }
                }
            },
            "PaymentInformation": {
                "ShipmentCharge": {
                    "Type": "01",
                    "BillShipper": {
                        "AccountNumber": "43X322"
                    }
                }
            },
            "Service": {
                "Code": "11",
                "Description": ""
            },
            "Package": [
                {
                    "Description": "Products from Driftworks",
                    "Packaging": {
                        "Code": "02",
                        "Description": ""
                    },
                    "Dimensions": {
                        "UnitOfMeasurement": {
                            "Description": "Centimetres",
                            "Code": "CM"
                        },
                        "Length": "25.0",
                        "Width": "24.0",
                        "Height": "13.0"
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Description": "Kilograms",
                            "Code": "KGS"
                        },
                        "Weight": "1"
                    }
                },
                {
                    "Description": "Products from Driftworks",
                    "Packaging": {
                        "Code": "02",
                        "Description": ""
                    },
                    "Dimensions": {
                        "UnitOfMeasurement": {
                            "Description": "Centimetres",
                            "Code": "CM"
                        },
                        "Length": "39.0",
                        "Width": "23.0",
                        "Height": "18.0"
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Description": "Kilograms",
                            "Code": "KGS"
                        },
                        "Weight": "1.8"
                    }
                },
                {
                    "Description": "Products from Driftworks",
                    "Packaging": {
                        "Code": "02",
                        "Description": ""
                    },
                    "Dimensions": {
                        "UnitOfMeasurement": {
                            "Description": "Centimetres",
                            "Code": "CM"
                        },
                        "Length": "20.0",
                        "Width": "20.0",
                        "Height": "20.0"
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Description": "Kilograms",
                            "Code": "KGS"
                        },
                        "Weight": "5.0"
                    }
                }
            ],
            "ShipmentServiceOptions": {
                "DeliveryConfirmation": {
                    "DCISType": 1
                }
            },
            "ShipmentRatingOptions": {
                "NegotiatedRatesIndicator": {},
                "UserLevelDiscountIndicator": {},
                "RateChartIndicator": {}
            }
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

res = ups.send_payload(url, payload)

print(res)