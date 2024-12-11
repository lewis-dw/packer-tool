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
    changes = session.pop('changed_vals', {})
    shipper = request.cookies.get('current_shipper')


    # if there is data then proceed
    if data:
        # after verification proceed to quote the order using concurrent futures
        update_log.create_log_line('actions', f"`{shipper}` attempting to quote {data['order_name']} to {data['shipping_country']} ({data['shipping_country_id']}).")
        all_quotes = []
        all_errors = []
        with ThreadPoolExecutor() as executor:
            future_to_service = {
                executor.submit(fedex.quote_order, deepcopy(data)): 'FedEx',
                executor.submit(ups.quote_order, deepcopy(data)): 'UPS'
            }

            # process results as they complete
            for future in as_completed(future_to_service):
                service_name = future_to_service[future] # pull this in case i want to debug which has completed
                quote = future.result()
                if quote['state'] == 'Success':
                    all_quotes.extend(quote['value'])
                else:
                    all_errors.extend(quote['value'])


        # log the quoting results
        update_log.create_log_line('actions', f'{len(all_quotes)} valid. {len(all_errors)} errors.')


        # parse the quote results then display to the user
        quote_content, error_content = shipping_functions.parse_quotes({'quotes':all_quotes, 'errors':all_errors})
        data = {
            'order_id': data['order_name'],
            'country_to': data['shipping_country'],
            'quote_content': quote_content,
            'error_content': error_content
        }

        return render_template('quote_order.html', data=data, changes=changes)

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
    printer_loc = request.args.get('printer_loc')
    label_size = request.args.get('label_size')
    shipper = request.cookies.get('current_shipper')


    # only proceed if there is currently data
    if data:
        # log the action
        update_log.create_log_line('actions', f'`{shipper}` attempting to ship with {courier} using {shipping_code}.')

        # ups
        if courier == 'UPS':
            res = ups.ship_order(data, shipping_code)

        # fedex
        elif courier == 'FEDEX':
            res = fedex.ship_order(data, shipping_code, label_size)

    # if they access the page with no data redirect them back to the dashboard
    else:
        return redirect('/')


    # deal with result of a successful ship and log a message respective of what happened
    if res['state'] == 'Error':
        errors = res['value']
        ship_result = f'Failed with {courier}. Error/s: {errors}'
    else:
        master_id = res['value']['master_id']
        labels = res['value']['labels']
        ship_result = f'Successfully shipped with {courier}. Tracking number: {master_id}'

    # log the event
    update_log.create_log_line('actions', res['state'])
    update_log.create_log_line('results', ship_result)


    # if success then we need to also print the labels out
    if res['state'] == 'Success':
        # loop over labels
        for label_id, label_dict in enumerate(labels):
            # print the label
            print_res = shipping_functions.print_label(label_dict['label_data'], printer_loc, label_size, label_dict['label_name'])

            # deal with result of printing the label
            initial_message = f'Label {label_id}/{len(labels)} for {master_id}'
            if print_res['state'] == 'Error':
                update_log.create_log_line('results', f"{initial_message} failed to print. Reason: {print_res['value']}")
            else:
                update_log.create_log_line('results', f'{initial_message} succeeded in printing.')


    # render the results to the user
    return render_template('ship_order.html', data=ship_result)