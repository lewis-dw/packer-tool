from flask import Blueprint, request, redirect, render_template, session, url_for
from app.odoo.api import get_orders, get_specific_order, clean_data
from app.shipping import fedex, ups

"""
These routes are used for quoting and shipping an order
"""
shipping = Blueprint('shipping', __name__, template_folder='templates/shipping')





"""
Get and display all info about the order
"""
@shipping.route('/quote_order')
def quote_order():
    # get the currently loaded data from flask session
    data = session.get('data', {})

    # if there is data then display it to user
    if data:
        return render_template('quote_order.html')

    # if user tried to load the page with no data in the session then they need to be redirected back to the dashboard
    else:
        return redirect('/')