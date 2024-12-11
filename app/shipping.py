from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from flask import Blueprint, request, redirect, render_template, session
from app.shipper import fedex, ups, shipping_functions
from app.logger import update_log

"""
These routes are used for quoting and shipping an order
"""
shipping = Blueprint('shipping', __name__, template_folder='templates/shipping', static_folder='static')


# run this to get all the jsons we want
province_lookup = shipping_functions.get_all_yamls('province_lookup')





"""
Process the data before quoting the data with every courier
"""
@shipping.route('/process_data')
def process_data():
    # get the currently loaded data from flask session
    data = session.get('order_data', {})


    # if there is data then proceed
    if data:
        # after verification proceed to quote the order using concurrent futures
        update_log.create_log_line(f"Attempting to quote {data['order_name']} to {data['shipping_country']} ({data['shipping_country_id']}).")
        all_quotes = []
        all_errors = []
        with ThreadPoolExecutor() as executor:
            future_to_service = {
                executor.submit(fedex.quote_order, deepcopy(data)): 'FedEx',
                executor.submit(ups.quote_order, deepcopy(data)): 'UPS'
            }

            # process results as they complete
            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                print(service_name)
                quote = future.result()
                if quote['state'] == 'Success':
                    all_quotes.extend(quote['value'])
                else:
                    all_errors.extend(quote['value'])


        # log the quoting results
        update_log.create_log_line(f'Successful quotes: {all_quotes}')
        if all_errors:
            update_log.create_log_line(f'Errors: {all_errors}')

        # parse the quote results then display to the user
        quote_content, error_content = shipping_functions.parse_quotes({'quotes':all_quotes, 'errors':all_errors})
        data = {
            'order_id': data['order_name'],
            'country_to': data['shipping_country'],
            'quote_content': quote_content,
            'error_content': error_content
        }

        return render_template('quote_order.html', data=data)

    # else just redirect them back to the homepage they shouldnt be here
    else:
        return redirect('/')





"""
This page handles the user selecting a shipping method from the quote page
"""
@shipping.route('/select_method')
def select_method():
    # get the args and set vars
    data = session.get('order_data', {})
    courier = request.args.get('courier').upper()
    shipping_code = request.args.get('shipping_code')
    shipper = request.cookies.get('current_shipper')
    res = {'state': 'Error', 'value': 'Missing order data'}


    # only proceed if there is currently data
    if data:
        # log the action
        update_log.create_log_line(f'{shipper} attempting to ship with {courier} using {shipping_code}.')

        # ups
        if courier == 'UPS':
            res = ups.ship_order(data, shipping_code)

        # fedex
        elif courier == 'FEDEX':
            res = fedex.ship_order(data, shipping_code, '4x6')


    # handle the result
    if res['state'] == 'Error':
        errors = res['value']
        ship_result = f'Failed with {courier}. Error/s: {errors}'

    else:
        master_id = res['value']['master_id']
        ship_result = f'Successfully shipped with {courier}. Tracking number: {master_id}'


    # log the action
    update_log.create_log_line(ship_result)
    return redirect('/')