import os
import pathlib
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta


# load .env variables
load_dotenv()
api_key = os.getenv('CLICKUP_API_KEY')
list_id = os.getenv('CLICKUP_LIST_ID')


# create the url and headers for requests
url = f'https://api.clickup.com/api/v2/list/{list_id}/task'
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json",
}


# vars
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))





def next_friday():
    # figure out how far away next friday is in days
    now = datetime.now()
    days_until_friday = (4 - now.weekday() + 7) % 7  # 4 represents Friday

    # if it is already friday and past 16:00 then skip to the next friday
    if days_until_friday == 0 and now.hour >= 16:
        days_until_friday = 7

    # find next friday and the time at 16:00 then convert to milliseconds from epoch
    next_friday = now + timedelta(days=days_until_friday)
    next_friday = next_friday.replace(hour=16, minute=0, second=0, microsecond=0) # %Y-%m-%d %H:%M:%S
    return int(next_friday.timestamp() * 1000) # convert to milliseconds from epoch





def create_task(sku, message):
    """
    Creates a clickup task with the inputted sku and message

    Args:
        sku (str): The product sku with an issue.
        message (str): A description of what is wrong with the product.

    Returns:
        str: The status of the task creation.
    """
    # send the task creation if data is valid
    if sku:
        # generate payload
        payload = {
            "name": f'Product SKU: {sku}',
            "description": message,
            "assignees": [32508419],
            "tags": [],
            "status": "to do",
            "priority": 1,
            "due_date": next_friday()
        }

        # send request and catch response
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            res = 'Report successfully submitted'
        else:
            res = res.json()['err']

    else:
        res = 'Product SKU field is empty'
    return res