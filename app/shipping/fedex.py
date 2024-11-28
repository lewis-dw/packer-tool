import os
from dotenv import load_dotenv
from shipping_functions import join_url, get_shipping_date

# load env variables and set if using live or test
load_dotenv()
prefix = 'TEST_'

# get the url parts
base_url = os.getenv(f'{prefix}FEDEX_BASE_URL')
auth_url = os.getenv(f'{prefix}FEDEX_OAUTH_URL')
label_url = os.getenv(f'{prefix}FEDEX_LABEL_URL')
quote_url = os.getenv(f'{prefix}FEDEX_QUOTE_URL')
void_url = os.getenv(f'{prefix}FEDEX_VOID_URL')

# get the credentials
_id = os.getenv(f'{prefix}FEDEX_ID')
secret = os.getenv(f'{prefix}FEDEX_SECRET')
account_id = os.getenv(f'{prefix}FEDEX_ACCOUNT_ID')


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
            "shipDateStamp": get_shipping_date('fedex'),
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
    return payload

# if shipping any of these countries then the statecode is required
if data['shipping_country_id'] in ["IE", "US", "CA"] and .shipping_address_statecode == "":
    # if country to ship to is ireland then need to find a province code
    if .shipping_address_country == "IE":
        result = get_eircode(.shipping_address_postcode)

    # if country to ship to is USA or canada then need to find a state code
    elif .shipping_address_country in ["US", "CA"]:
        result = get_statecode(.shipping_address_country, .shipping_address_postcode)

    if "Error" in result:
        print(result)
        # methods failed so prompt the user
        result = check_state(.shipping_address_line3,
                                .shipping_address_city,
                                .shipping_address_country)
    .shipping_address_statecode = result
    payload["requestedShipment"]["recipient"]["address"]["stateOrProvinceCode"] = result

if .shipping_address_country in ["IE", "US",
                                                "CA"] and .shipping_address_statecode != "":
    payload["requestedShipment"]["recipient"]["address"][
        "stateOrProvinceCode"] = .shipping_address_statecode
