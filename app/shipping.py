from flask import Blueprint, request, redirect, render_template, session, url_for
from app.shipper import fedex, ups, shipping_functions

"""
These routes are used for quoting and shipping an order
"""
shipping = Blueprint('shipping', __name__, template_folder='templates/shipping', static_folder='static')


# run this to get all the jsons we want
province_lookup = shipping_functions.get_all_yamls('province_lookup')





"""
Process the data before taking the desired action on the data
"""
@shipping.route('/process_data')
def process_data():
    # get the currently loaded data from flask session
    data = session.get('order_data', {})
    action_type = request.args.get('action_type')
    print(action_type)


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

        # parse the quote results
        quote_content, error_content = shipping_functions.parse_quotes({'quotes':all_quotes, 'errors':all_errors})
        data = {
            'order_id': data['order_name'],
            'country_to': data['shipping_country'],
            'quote_content': quote_content,
            'error_content': error_content
        }

        # if the action type was just to quote the order then just display it to the user
        if action_type == 'quote':
            return render_template('quote_order.html', data=data)

        # if the action type was to quote the order then
        elif action_type == 'ship':
            return render_template('error.html', error_reason='HELLOO')

    # all other hanging else statements should lead to here
    return redirect('/')