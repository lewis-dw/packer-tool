from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from app.odoo.api import get_orders, get_specific_order, clean_data
from app.shipper import shipping_functions
from app.clickup.api import create_task

"""
These routes are used for when getting orders from odoo
"""
orders = Blueprint('orders', __name__, template_folder='templates/orders', static_folder='static')


# we want to load our yamls into json format
state_codes = shipping_functions.get_all_yamls('state_codes')





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
Allow user to select the correct statecode for country code
"""
@orders.route('/select_statecode')
def select_statecode():
    data = session.get('partial_order_data', {})

    # if data exists then load the page and pass in all the statecodes to choose from
    if data:
        return render_template('select_statecode.html', codes=state_codes)
    else:
        return redirect('/')





"""
Clean the order data before saving it to current session
"""
@orders.route('/load_order', methods=['GET', 'POST'])
def load_order():
    # load the data in via an api call and attempt to do the initial clean
    if request.method == 'GET':
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

            # if the statecode retrieval failed then the user needs to do it manually
            if data['shipping_statecode'] == 'manual':
                session['partial_order_data'] = data
                return redirect(url_for('orders.select_statecode'))

        # on fail we want to display to the user the error of their ways
        else:
            return render_template('no_order_found.html', order_id=order_id)


    # alternatively if the method to access this page was via a post request,
    # then it means they are already after the initial clean but the statecode retrieval failed
    elif request.method == 'POST':
        # load the partial_order_data back and get the selected statecode
        data = session.get('partial_order_data', {})

        # if there was no data then redirect user to dashboard
        if not data:
            session.clear()
            return redirect('/')

        # if there was data then save the selected statecode and continue
        else:
            data['shipping_statecode'] = request.form.get('state_code')


    # not sure how the user would trigger this but we need to catch it before we continue
    else:
        return redirect('/')


    # once the data is all cleaned and stuff we want to clear the current session data and save the data
    session.clear()
    session['order_data'] = data
    return redirect(url_for('orders.display_order'))





"""
Get and display all info about the order
"""
@orders.route('/display_order')
def display_order():
    # get the currently loaded data from flask session
    data = session.get('order_data', {})
    errors = session.pop('required_fields', {})

    # if there is data then display it to user
    if data:
        return render_template('display_order.html', order=data, errors=errors)

    # if user tried to load the page with no data in the session then they need to be redirected back to the dashboard
    else:
        return redirect('/')





"""
Save the currently loaded data from the 'display order' page
"""
@orders.route('/save_order', methods=['POST'])
def save_order():
    # these are the key cols that are not allowed to be empty
    key_cols = {
        # shipping info
        'shipping_street': '',
        'shipping_postcode': '',

        # invoice lines
        'product_sku': '',
        'product_demand_qty':'',
        'unit_price': '',
        'unit_weight':'',
        'product_height':'',
        'product_width':'',
        'product_length':'',

    }
    missing_vals = False

    # we will update the session data with what we got returned from the post form
    data = session.get('order_data', {})


    # if there is not session order data then we want to redirect but if there is we can proceed
    if data:
        for key, value in request.form.items():
            # format value to correct data type that it should be eg str(1.0) -> int(1)
            value = str(value).strip()


            # order commercial invoice lines
            if key.startswith('line-'):
                # extract the key name and index from the key
                true_key, index = key.rsplit('_', 1)
                true_key = true_key.split('-')[1]
                index = int(index) - 1
                data['commercial_invoice_lines'][index][true_key] = value

            # all other values
            else:
                true_key = key
                data[key] = value


            # if the key was a key col and the value was empty then need to update the missing cols
            if true_key in key_cols.keys() and value == '':
                missing_vals = True
                key_cols[key] = 'Required'


        # this needs to be separate due to checkbox behaviour
        data['etd_required'] = request.form.get('etd_required', 'off')

        # update session order data regardless if they are missing data or not
        session.clear()
        session['order_data'] = data


        # if there were missing values then we need to re-render the page with the missing cols highlighted
        if missing_vals:
            session['required_fields'] = key_cols
            return redirect(url_for('orders.display_order'))

        # if all required fields were entered then redirect user
        else:
            return redirect(url_for('shipping.process_data'))
    else:
        return redirect('/')





"""
Submit the report task to clickup
"""
@orders.route('/report_issue', methods=['POST'])
def report_issue():
    data = request.json
    res = create_task(data['sku'], data['message'])
    return jsonify({"response": res})