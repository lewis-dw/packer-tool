from flask import Blueprint, request, redirect, render_template, session, url_for
from app.odoo.api import get_orders, get_specific_order, clean_data
from app.shipper import fedex, ups, shipping_functions

"""
These routes are used for quoting and shipping an order
"""
shipping = Blueprint('shipping', __name__, template_folder='templates/shipping')





"""
Handle what the user selected as the statecode
"""
@shipping.route('/handle_statecode', methods=['POST'])
def handle_statecode():
    # get the result of user selecting statecode
    data = session.get('data', {})
    if data:
        data['shipping_statecode'] = request.form.get('order_id')
        session['data'] = data
        redirect_dest = session.get('verify_from', '/')
        return redirect(url_for(f'shipping.{redirect_dest}'))
    else:
        return redirect('/')





"""
Allow user to select the correct statecode for country code
"""
@shipping.route('/select_statecode')
def select_statecode():
    data = session.get('data', {})
    if data:
        return render_template('select_statecode.html')
    else:
        return redirect('/')





"""
Redirect used to verify the data is valid and has all values it needs to be processed
"""
@shipping.route('/verify_data')
def verify_data():
    # get order data from session and verify it exists
    data = session.get('data', {})
    if data:
        # need to check if the data needs a shipping statecode and doesnt have one assigned yet
        if data['shipping_country_id'] in ['IE', 'US', 'CA'] and data.get('shipping_statecode', '') == '':
            result = shipping_functions.find_statecode(data)
            if result['state'] == 'Success':
                data['shipping_statecode'] = result['value']
            else:
                # redirect user to the statecode setter page
                return redirect(url_for('shipping.select_statecode'))


        # after finishing set the dw_verified state and update the order data in the session var
        data['dw_verified'] = 'True'
        session['data'] = data

    # if no data then redirect to dashboard as they shouldnt be here
    else:
        return redirect('/')

    # grab where the redirect was from and redirect back
    redirect_dest = session.get('verify_from', '/')
    return redirect(url_for(f'shipping.{redirect_dest}'))





"""
Display the results of quoting the order
"""
@shipping.route('/quote_order')
def quote_order():
    # get the currently loaded data from flask session
    data = session.get('data', {})


    # if there is data then display it to user
    if data:
        # check if the data has been verified yet
        if data.get('dw_verified', '') == '':
            session['verify_from'] = 'quote_order'
            return redirect(url_for('shipping.verify_data'))
        session.pop('verify_from', None)

        # after verification proceed to quote the order
        res, data = fedex.quote_order(data)
        session['data'] = data # in case the statecode was added it gets updated for the session
        return render_template('quote_order.html')

    # if no data then redirect to dashboard as they shouldnt be here
    else:
        return redirect('/')