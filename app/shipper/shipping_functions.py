from datetime import datetime, timedelta
import os
import pathlib
import yaml
import html
import requests
import time
from app.logger import update_log

# database
from app import db
from app.models import ShippingCodes, ShippingHistory, Labels, Countries, StateCodes


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





def get_shipping_date(end_time, days_penalty, date_format):
    """
    Gets the ship date for a quote/ship call

    Expected:
        FedEx           12:00, 1, %Y-%m-%d
        UPS:            16:00, 1, %Y%m%d
        Royal Mail:     16:00, 1, ---
        Free Shipping:  00:01, 2, ---

    Args:
        end_time (str): Latest time in the day before the order gets the day penalty added. Example: "17:30"
        days_penalty (int): The number of days to add to current date if the current time is past the end_time.
        date_format (str): A date format string for how the date should be returned as. Example: "%Y-%m-%d"

    Returns:
        str: The shipping date in the correct format and with the day penalty.
        str: The shipping date in a normal format and with the day penalty.
    """
    # format the input end time
    end_time = datetime.strptime(end_time, "%H:%M").time()
    now = datetime.now()

    # check if the curent time is over the end time, if so then add the days penalty
    if now.time() >= end_time:
        new_date = now + timedelta(days=days_penalty)
    else:
        new_date = now
    return new_date.strftime(date_format), new_date.strftime(r'%Y-%m-%d')





def parse_quotes(data):
    """
    Just parses through the quotes and errors to format it into something displayable
    """
    # parse quotes
    if data['quotes']:
        # sort the quotes by cost
        quotes = sorted(
            data['quotes'], 
            key=lambda x: float(x['cost'])
        )

        # loop over the quotes after sorting and build up a html table
        table_html = []
        for quote in quotes:
            # extract data
            courier = html.escape(quote['courier'].upper())
            shipping_code = html.escape(quote['shipping_code'])
            cost = html.escape(str(quote['cost']))
            sat_indicator = html.escape(str(quote['sat_indicator']))

            # need to translate the shipping code
            code_query = ShippingCodes.query.filter(ShippingCodes.shipping_code == f'{shipping_code}{sat_indicator}').first()
            if code_query is not None: # match
                friendly_code = code_query.friendly_code
            else: # no match
                friendly_code = shipping_code

            # construct table line and log to success
            html_row = ''.join([
                f'<tr onclick="rowClicked(\'{courier}\', \'{shipping_code}\', \'{sat_indicator}\', \'{cost}\')">',
                f'<td>{courier}</td><td>{friendly_code}</td><td>{cost}</td>',
                '</tr>'
            ])
            table_html.append(html_row)
            update_log.create_log_line('results', f'Success: {courier} - {shipping_code} - {cost} - {sat_indicator}')

        quote_content = ''.join([
            '<table>',
            '<thead><tr><th>Courier</th><th>Method</th><th>Cost</th></tr></thead>',
            '<tbody>',
            ''.join(table_html),
            '</tbody></table>',
        ])

    else:
        quote_content = '<p>No quotes succeeded</p>'


    # parse errors
    if data['errors']:
        # construct the error table content
        table_html = []
        for error in data['errors']:
            courier = error['courier'].upper()
            message = error['error']

            # construct table line and log the error
            table_html.append(f"<tr><td>{courier}</td><td>{message}</td></tr>")
            update_log.create_log_line('results', f'Fail: {courier} - {message}')

        # construct the whole error table
        error_content = ''.join([
            '<table>',
            '<thead><tr><th>Courier</th><th>Error</th></tr></thead>',
            '<tbody>',
            ''.join(table_html),
            '</tbody></table>',
        ])
    else:
        error_content = '<p>No errors during quoting</p>'

    return quote_content, error_content





def download_with_retries(url, delay=0.5, max_retry=10):
    """
    Download the content from a url and keep retrying until successful up to a limit.
    Returns the raw content from the url.
    """

    for attempt in range(max_retry):
        time.sleep(delay)
        res = requests.get(url)
        if res.status_code == 200:
            return {'state': 'Success', 'value': res}
    return {'state': 'Error', 'value': f'Max retries hit ({max_retry})'}


########################################################################################################################################################################
# Database updates


def update_outs_table(data, shipper, courier, shipping_code, master_id, ship_at, dw_paid, commercial_invoice):
    db.session.add(ShippingHistory(
        order_name = data['order_name'],
        out_id = 'xxx',
        processed_at = datetime.now(),
        shipped_at = ship_at,
        shipper = shipper,
        name = data['shipping_name'],
        company = data['shipping_company'],
        shipped_to = data['shipping_country_id'],
        customer_paid = data['shipping_cost'],
        dw_paid = float(dw_paid),
        tracking_number = master_id,
        courier = courier,
        method = shipping_code,
        commercial_invoice = commercial_invoice,
    ))
    db.session.commit()



def update_labels_table(data, master_id, label_id, zpl_data, courier, shipping_code):
    db.session.add(Labels(
        order_name = data['order_name'],
        tracking_number = master_id,
        label_id = label_id,
        zpl_data = zpl_data,
        courier = courier,
        method = shipping_code
    ))
    db.session.commit()


########################################################################################################################################################################
# Database queries


def get_state_code(region_name):
    """
    Returns the statecode for a given region
    """

    # query the table
    state_code = StateCodes.query.filter(
        StateCodes.region_name == str(region_name).upper()
    ).with_entities(StateCodes.state_code).first()
    return state_code


def get_country_code(country):
    """
    Returns the country code for a given country for the invoice items
    """

    # query the table
    country_code = Countries.query.filter(
        Countries.country_name == country
    ).with_entities(Countries.shipping_country_code).first()
    return country_code


def get_all_country_codes():
    # query the table
    results =  Countries.query.with_entities(Countries.country_name, Countries.shipping_country_code).all()
    country_dict = {country_id: country_name for country_name, country_id in results}
    return country_dict




def get_labels_for_order(order_id):
    """
    get all labels related to the order_id passed
    """

    # query the table
    results = Labels.query.filter(
        Labels.order_name == order_id
    ).all()

    # parse the results
    if results:
        return {'state': 'Success', 'value': results}
    else:
        return {'state': 'Error', 'value': f'No labels found for order name: {order_id}'}
