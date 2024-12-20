from app.odoo.api import send_ship_message, send_pack_message, join_url
# send_ship_message('S125951', 'FEDEX', '794812295004')

order_data = {
    'pack_id': 'WH/PACK/13765',
    'done_items_message': 'DW-S-SB03-04-BLK-NRE (1x) | DW-ROSE-M16-RH (1x) | DW-S-ARMS-TOERODCOLLET (2x)',
    'order_items': [
        {
            "product_id": 11901,
            "qty_done": 1
        },
        {
            "product_id": 139,
            "qty_done": 1
        },
        {
            "product_id": 65,
            "qty_done": 2
        }
    ]
}

send_pack_message('S125999', 'Hayden', order_data)


# https://dw-uat.glodo.cloud//dwapi/v1/orders/S125999/pack