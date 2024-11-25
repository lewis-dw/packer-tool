from flask import Blueprint, render_template, jsonify
from . import db
from app.odoo.get_orders import get_orders

main = Blueprint('main', __name__)



@main.route('/')
def index():
    return render_template('dashboard.html')



@main.route('/page_1/')
def page_1(user='Lewis'):
    return render_template('page_1.html', user=user)



@main.route('/shipper/')
def shipper_page():
    return render_template('shipper.html')



@main.route('/orders/') # result, data = get_first_order(data)
def valid_orders():
    # get valid orders
    result, data = get_orders()

    # show the valid orders to user
    if result == 'Success':
        return render_template('orders.html', orders=data)

    # need to redirect them to a page they can use to refresh which will reload this page
    elif result == 'Fail':
        print(data)



# for loading most recent shipping data
@main.route('/api/shipments/', methods=['GET'])
def get_shipments():
    from .models import ShippedOrders # lazy import to avoid circular import issues
    shipments = ShippedOrders.query.order_by(ShippedOrders.date.desc()).limit(30).all()
    data = [
        {
            'date': shipment.date.strftime('%Y-%m-%d %H:%M:%S'),
            'orderId': shipment.order_id,
            'name': shipment.name,
            'company': shipment.company,
            'postagePaid': shipment.postage_paid,
            'shippingCost': shipment.shipping_cost,
            'shipmentId': shipment.tracking_number,
            'status': shipment.status,
            'carrier': shipment.carrier,
            'serviceType': shipment.service_type
        }
        for shipment in shipments
    ]
    return jsonify(data)