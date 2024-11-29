from flask import Blueprint, request, redirect, render_template, session, url_for
from app.odoo.api import get_orders, get_specific_order, clean_data

"""
These routes are used for when getting orders from odoo
"""
orders = Blueprint('orders', __name__, template_folder='templates/orders', static_folder='static')





"""
Get and display all current valid orders
"""
@orders.route('/all_orders')
def all_orders():
    result, data = get_orders()

    # show the valid orders to user
    if result == 'Success':
        return render_template('all_orders.html', orders=data)

    # need to redirect them to a page they can use to refresh which will reload this page
    elif result == 'Fail':
        return render_template('error.html', error_reason=data)





"""
Render the page that allows user to type in an order id or scan one in
"""
@orders.route('/manual_search')
def manual_search():
    return render_template('manual_search.html')





"""
Receive the order id from the row click
"""
@orders.route('/get_order_id/<order_id>')
def get_order_id(order_id):
    # Redirect directly to the desired URL
    return redirect(url_for('orders.load_order', order_id=order_id))





"""
Receive the order id from the manual entry/rdt scan in
"""
@orders.route('/get_manual_entry', methods=['POST'])
def get_manual_entry():
    order_id = request.form.get('order_id')
    # Redirect directly to the desired URL
    return redirect(url_for('orders.load_order', order_id=order_id))





"""
Clean the order data before saving it to current session
"""
@orders.route('/load_order')
def load_order():
    # get the order_id from query
    order_id = request.args.get('order_id')

    # attempt to load the data on the order via its id
    status, data = get_specific_order(order_id)

    # on success then we need to run some cleaning functions on it before storing it in a flask session
    if status == 'Success':
        # rename the items key as it causes issues
        data['order_items'] = data.pop('items')

        # clean the data up
        data = clean_data(data)

        # set session 'data' to the order data
        session['data'] = data

        # finally redirect them to the display order page
        return redirect(url_for('orders.display_order'))

    # if it errored then redirect to the no order found error page
    else:
        return render_template('no_order_found.html', order_id=order_id)





"""
Get and display all info about the order
"""
@orders.route('/display_order')
def display_order():
    # get the currently loaded data from flask session
    data = session.get('data', {})

    # if there is data then display it to user
    if data:
        return render_template('display_order.html', order=data)

    # if user tried to load the page with no data in the session then they need to be redirected back to the dashboard
    else:
        return redirect('/')





"""
Save the currently loaded data from the 'display order' page
"""
@orders.route('/save_order', methods=['POST'])
def save_order():
    # we will update the session data with what we got returned from the post form
    data = session.get('data', {})


    # if there is not session order data then we want to redirect but if there is we can proceed
    if data:
        for key, value in request.form.items():
            # format value to correct data type that it should be eg str(1.0) -> int(1)
            value = str(value)
            if value.replace('.', '').replace(' ', '').isdigit():
                value = float(value)
                if value.is_integer():
                    value = int(value)


            # order commercial invoice lines
            if key.startswith('line-'):
                # extract the key name and index from the key
                key, index = key.rsplit('_', 1)
                key = key.split('-')[1]
                index = int(index) - 1
                data['commercial_invoice_lines'][index][key] = value


            # order items
            elif key.startswith('item-'):
                # extract the key name and index from the key
                key, index = key.rsplit('_', 1)
                key = key.split('-')[1]
                index = int(index) - 1
                data['order_items'][index][key] = value


            # all other values
            else:
                data[key] = value


        # reset the session order data and redirect user
        session.clear()
        session['data'] = data
        return redirect(url_for('shipping.quote_order'))
    else:
        return redirect('/')