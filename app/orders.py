from flask import Blueprint, request, redirect, render_template, session, url_for, jsonify
from app.odoo.api import get_orders, get_specific_order, clean_data
from app.clickup.api import create_task
from app.logger import update_log
from app.models import Countries, CountryFlags, CommodityCodes

"""
These routes are used for when getting orders from odoo
"""
orders = Blueprint('orders', __name__, template_folder='templates/orders', static_folder='static')





"""
Get and display all current valid orders
"""
@orders.route('/all_orders')
def all_orders():
    res = get_orders()

    # show the valid orders to user
    if res['state'] == 'Success':
        return render_template('all_orders.html', orders=res['value'])

    # need to redirect them to a page they can use to refresh which will reload this page
    elif res['state'] == 'Error':
        return render_template('error.html', error_reason=res['value'])





"""
Render the page that allows user to type in an order id or scan one in
"""
@orders.route('/manual_search')
def manual_search():
    action = request.args.get('action')
    if action:
        return render_template('manual_search.html', action=action)
    else:
        return redirect('/')





"""
Receive the order id from however the user has entered it
"""
@orders.route('/get_order_id', methods=['GET', 'POST'])
def get_order_id():
    # get the order id however it was passed in and handle anything else
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        action = request.form.get('action')
    elif request.method == 'GET':
        order_id = request.args.get('order_id')
        action = 'search_order'
    else:
        return redirect('/')


    # first verify they actually searched for something
    if order_id:
        # if the action is to search for order then try to find an order by that id
        if action == 'search_order':
            res = get_specific_order(order_id)

            # on fail we want to display to the user the error of their ways
            if res['state'] == 'Error':
                return render_template('bad_search.html', message=f'I couldn\'t find an order with the ID: {order_id}', _from='search_order')

            # if it succeeded then load it into the session
            else:
                session['partial_order_data'] = res['value']
                session['original_order_data'] = res['value']
                # Redirect directly to the desired URL
                return redirect(url_for('orders.load_order'))


        # redirect to the reprint label page to handle this request
        elif action == 'reprint_label':
            return redirect(url_for('shipping.reprint_label', order_id=order_id))


        # redirect to the commercial invoice page to handle this request
        elif action == 'get_invoice':
            return redirect(url_for('shipping.get_invoice', order_id=order_id))


        # not sure how the user would trigger this but we need to catch it before we continue
        else:
            return redirect('/')

    # if they didnt search for anything redirect back to manual search
    else:
        return redirect(url_for('orders.manual_search', action=action))





"""
We need the user to do some manual selections
"""
@orders.route('/user_intervention')
def user_intervention():
    data = session.get('partial_order_data', {})

    # if data exists then load the page and pass in all information it could require
    if data:
        state_codes = Countries.get_all_country_codes()
        commodity_codes = CommodityCodes.get_all_codes()
        return render_template('user_intervention.html', data=data, codes=state_codes, commodity_codes=commodity_codes)
    else:
        return redirect('/')





"""
Clean the order data before saving it to current session
"""
@orders.route('/load_order', methods=['GET', 'POST'])
def load_order():
    # load the data in via an api call and attempt to do the initial clean
    if request.method == 'GET':
        # load in the order_data
        data = session.pop('partial_order_data', {})

        # can only proceed if there is data
        if not data:
            session.clear()
            return redirect('/')

        else:
            # rename the items key as it causes issues
            data['order_items'] = data.pop('items')

            # clean the data up and deal with the result
            result = clean_data(data)

            if result['state'] == 'Success':
                data, user_intervention = result['value']

                # if there is a need for user intervention then display the page for it and handle the specifics there
                if user_intervention:
                    session['partial_order_data'] = data
                    return redirect(url_for('orders.user_intervention'))

            else:
                print(result['value'])
                return redirect('/')

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
            # loop over the form data and if the value is one that will update the order_data then proceed to do that
            for k, value in request.form.items():
                if '|' in k:
                    # extract the key and key and the sku to update
                    key, sku = k.split('|')

                    # loop over the items to update the values
                    for line in data['commercial_invoice_lines']:
                        if line['product_sku'] == sku:
                            line[key] = value

            # update state code if it exists
            if request.form.get('state_code'):
                data['shipping_statecode'] = request.form.get('state_code')


    # not sure how the user would trigger this but we need to catch it before we continue
    else:
        return redirect('/')


    # once the data is all cleaned and stuff we want to clear the current session data and save the data
    session.pop('order_data', None)
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
        # find the svg data for the country id then render the page
        svg_data = CountryFlags.get_flag_svg(data['shipping_country_id'])
        return render_template('display_order.html', order=data, svg_data=svg_data, errors=errors)

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
            # if the key is to be ignored then continue to the next one
            if key.endswith('-ignore'):
                continue

            # format value to correct data type that it should be eg str(1.0) -> int(1)
            value = str(value).strip()


            # this is for the following if statement to combine 2 similar statements into 1
            lookup_dict = {
                'line': 'commercial_invoice_lines',
                'item': 'order_items'
            }

            # parse commercial invoice line or the order item line
            if key.startswith('line-') or key.startswith('item-'):
                # extract the key name and index from the key
                true_key, index = key.rsplit('_', 1)
                group, true_key = true_key.split('-')
                group = lookup_dict[group]
                index = int(index) - 1
                data[group][index][true_key] = value

            # all other values
            else:
                # set vars
                true_key = key
                data[key] = value


            # if the key was a key col and the value was empty then need to update the missing cols
            if true_key in key_cols.keys() and value == '':
                missing_vals = True
                key_cols[key] = 'Required'


        # this needs to be separate due to checkbox behaviour
        data['etd_required'] = request.form.get('etd_required', 'off')


        # update session order data regardless if they are missing data or not
        session['order_data'] = data


        # if there were missing values then we need to re-render the page with the missing cols highlighted
        if missing_vals:
            session['required_fields'] = key_cols
            return redirect(url_for('orders.display_order'))

        # if all required fields were entered then redirect user
        else:
            return redirect(url_for('shipping.create_parcels'))
    else:
        return redirect('/')





"""
Submit the report task to clickup
"""
@orders.route('/report_issue', methods=['POST'])
def report_issue():
    # extract the data from the request
    sku = request.json['sku']
    message = request.json['message']
    shipper = request.cookies.get('current_shipper')

    # send the report and log the event
    res = create_task(sku, shipper, message)
    update_log.create_log_line('actions', f"`{shipper}` tried to report `{sku} - {message}`. Response: {res}")
    return jsonify({"response": res})