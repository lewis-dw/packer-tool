from clickupython import client, exceptions
import os
import pathlib
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta


# load .env variables
load_dotenv()
api_key = os.getenv('CLICKUP_API_KEY')
list_id = os.getenv('CLICKUP_LIST_ID')


# create client connection
c = client.ClickUpClient(api_key)


# vars
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))





def next_friday():
    # figure out when next friday is
    now = datetime.now()
    days_until_friday = (4 - now.weekday() + 7) % 7  # 4 represents Friday

    # if it is already friday and past 18:00 then skip to the next friday
    if days_until_friday == 0 and now.hour >= 18:
        days_until_friday = 7

    # calculate the next friday date and set the time for 18:00
    next_friday = (now + timedelta(days=days_until_friday)).strftime(r"%m-%d-%Y")
    return f'{next_friday} 18:00'





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
        try:
            res = c.create_task(
                list_id,
                name=f'Product SKU: {sku}',
                description=message,
                due_date=next_friday()
            ).json()

            # output the response for debugging
            res = json.loads(res)
            with open(os.path.join(debug_dir, 'clickup', 'clickup_res.json'), 'w') as f:
                json.dump(res, f, indent=4)

            # attempt to access parts of the clickup response
            if res.get('url', ''):
                res = 'Report successfully submitted'
            else:
                res = 'Something went wrong - tell Lewis'

        # catch clickup errors
        except exceptions.ClickupClientError as e:
            res = e.error_message
    else:
        res = 'Product SKU field is empty'
    return res