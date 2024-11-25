from flask import Blueprint, request, redirect, render_template, make_response
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
        return render_template('all_orders.html', orders=data)

    # need to redirect them to a page they can use to refresh which will reload this page
    elif result == 'Fail':
        return redirect('/dashboard/')





"""
Get and display all info about the order
"""
@orders.route('/display_order')
def display_order():
    # get the order_id from query
    order_id = request.args.get('order_id')

    print(order_id)

    # search the order_id passed in
    status, data = get_specific_order(order_id)

    # on success then pass in the whole json to the order page
    if status == 'Success':
        return render_template('display_order.html', order=data)
    else:
        return render_template('no_order_found.html', order_id=order_id)





"""
Receive the order id from the row click
"""
@orders.route('/get_order_id/<order_id>')
def get_order_id(order_id):
    # Redirect directly to the desired URL
    return redirect(f'/orders/display_order?order_id={order_id}')





"""
Receive the order id from the manual entry/rdt scan in
"""
@orders.route("/get_manual_entry/", methods=["POST"])
def get_manual_entry():
    order_id = request.form.get("order_id")
    # Redirect directly to the desired URL
    return redirect(f'/orders/display_order?order_id={order_id}')





"""
Render the page that allows user to type in an order id or scan one in
"""
@orders.route('/manual_search/')
def manual_search():
    return render_template('manual_search.html')