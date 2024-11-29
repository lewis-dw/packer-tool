from pgeocode import Nominatim
import requests
import re
from datetime import datetime, timedelta
import os
import pathlib
import yaml


# find the data dir
cur_dir = pathlib.Path(__file__).parent
data_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'data'))





def join_url(*url_parts):
    """
    Simple function to join all parts of the passed in url pieces and return
    This is because os.path.join doesnt work for URLs and i didnt want to muck about with other libraries when this is just as easy
    """
    url_parts = map(str, url_parts)
    full_url = '/'.join(url_parts).replace(' ', '%20')
    return full_url





def verify_line(name):
    """
    If any of the bad keywords are present in the name then return False
    """
    keywords = [
        ' fedex ', ' ups '
    ]
    if any(keyword in f' {name} '.lower() for keyword in keywords):
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
    """
    Returns the Irish county for a given postcode
    """
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
        return {'state':'Success', 'value':county}

    except Exception:
        # bad request error (key invalid or got blocked) are caught with this
        return {'state':'Error', 'value':'eircode failed'}





def get_statecode(country, post_code):
    """
    Returns the USA/Canada state code for a given post code
    """
    nomi = Nominatim(country)
    result = nomi.query_postal_code(post_code)
    state_code = str(result["state_code"])
    if state_code != "nan":
        return {'state':'Success', 'value':state_code}
    else:
        return {'state':'Error', 'value':'pgeocode failed'}





def find_statecode(data):
    """
    Depending on the country code, it will run the relevant 'get state code' function
    """
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





def get_country_code(country):
    """
    Returns the country code for a given country
    """
    # maybe inefficient but load the country_codes from yaml and search for the given country in there
    country_codes = get_all_yamls('country_codes')
    country_code = country_codes.get(country, country) # if it doesnt exist then just return the country
    return country_code






def get_all_yamls(*yamls):
    """
    For each file_name passed in, open the yaml file and return to user
    """
    results = []
    for file_name in yamls:
        with open(os.path.join(data_dir, f'{file_name}.yaml'), 'r') as file:
            results.append(yaml.safe_load(file))
    if len(results) == 1:
        results = results[0]
    return results





def parse_quotes(quotes):
    for quote in quotes:
        print(quote)