from flask import Blueprint, request, redirect, render_template
from app.odoo.api import get_orders, get_specific_order

"""
These routes are used for when getting orders from odoo
"""
orders = Blueprint('orders', __name__, template_folder='templates/orders')




"""
Get and display all current valid orders
"""
@orders.route('/all_orders/')
def all_orders():
    result, data = get_orders()

    # show the valid orders to user
    if result == 'Success':
        return render_template('orders.html', orders=data)

    # need to redirect them to a page they can use to refresh which will reload this page
    elif result == 'Fail':
        return redirect('/dashboard/')





"""
Get and display all info about the order
"""
@orders.route('/display_order')
def display_order():
    # get the order_id from query
    order_id = request.args.get('id')

    # search the order_id passed in
    status, data = get_specific_order(order_id)

    # on success then pass in the whole json to the order page
    if status == 'Success':
        print(order_id)
        return render_template('order.html', order=data)
    else:
        return redirect('/dashboard/')