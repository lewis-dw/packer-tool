from flask import Blueprint, request, redirect, render_template, session, url_for
from app.shipper import fedex, ups, shipping_functions

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
        # after verification proceed to quote the order
        fedex_result = fedex.quote_order(data)
        ups_result = ups.quote_order(data)

        # loop over all quotes and join the successful ones
        all_quotes = []
        all_errors = []
        for quote in [fedex_result, ups_result]:
            if quote['state'] == 'Success':
                all_quotes.extend(quote['value'])
            else:
                all_errors.extend(quote['value'])

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
    courier = request.args.get('courier')
    method = request.args.get('method')

    return {'courier': courier, 'method': method}