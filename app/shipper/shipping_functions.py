from pgeocode import Nominatim
import requests
import re
from datetime import datetime, timedelta





def join_url(*url_parts):
    """
    Simple function to join all parts of the passed in url pieces and return
    This is because os.path.join doesnt work for URLs and i didnt want to muck about with other libraries when this is just as easy
    """
    url_parts = map(str, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url





def verify_line(name):
    keywords = [
        'fedex', 'ups'
    ]
    if any(keyword in name.lower() for keyword in keywords):
        return False
    return True



def get_shipping_date(end_time, days_penalty, date_format):
    """
    Gets the ship date for a quote/ship call

    Expected:
        FedEx           12:00, 1, %Y-%m-%d
        UPS:            16:00, 1, ---
        Royal Mail:     16:00, 1, ---
        Free Shipping:  00:01, 2, ---

    Args:
        end_time (str): Latest time in the day before the order gets the day penalty added. Example: "17:30"
        days_penalty (int): The number of days to add to current date if the current time is past the end_time.
        date_format (str): A date format string for how the date should be returned as. Example: "%Y-%m-%d"

    Returns:
        str: The shipping date in the correct format and with the day penalty.
    """
    # format the input end time
    end_time = datetime.strptime(end_time, "%H:%M").time()
    now = datetime.now()

    # check if the curent time is over the end time, if so then add the days penalty
    if now.time() >= end_time:
        new_date = now + timedelta(days=days_penalty)
    else:
        new_date = now
    return new_date.strftime(date_format) # return the date in the requested format





def get_eircode(postcode):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    # get session key for eircode website
    url = "https://api-finder.eircode.ie/Latest/findergetidentity"
    response = requests.get(url, headers=header)
    try:
        key = response.json()["key"]
    except KeyError:
        return "Error: No key available from eircode"

    # send post code to the eircode website
    payload = {
        "key": key,
        "address": postcode,
        "language": "en",
        "geographicAddress": "true",
        "clientVersion": "388603cc"
    }
    url = "https://api-finder.eircode.ie/Latest/finderfindaddress"
    response = requests.get(url, payload, headers=header)



    try:  # try to get the postal address from the response
        postal = response.json()["postalAddress"]
        county = str(postal[-1]).upper().replace("CO. ", "")
        county = re.sub(r'\d+', '', county).strip()

        """do a database call here instead of dict lookups"""
        state_code = 'n/a'
        return {'state':'Success', 'value':state_code}

    except Exception:
        # bad request error (key invalid or got blocked) and keyerror (no address found) are caught with this
        return {'state':'Error', 'value':'eircode failed'}





def get_statecode(country, post_code):
    nomi = Nominatim(country)
    result = nomi.query_postal_code(post_code)
    state_code = str(result["state_code"])
    if state_code != "nan":
        return {'state':'Success', 'value':state_code}
    else:
        return {'state':'Error', 'value':'pgeocode failed'}





def find_statecode(data):
    # extract vars
    postcode = data['shipping_postcode']
    country_code = data['shipping_country_id']

    # run the country specific functions for statecode
    result = {'state':'Error', 'value':f'Invalid country code: {country_code}'}
    if country_code in ['IE']: # ireland
        result = get_eircode(postcode)

    elif country_code in ['US', 'CA']: # usa/canada
        result = get_statecode(country_code, postcode)

    return result