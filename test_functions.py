from app.odoo.api import send_ship_message, send_pack_message, join_url
# send_ship_message('S125951', 'FEDEX', '794812295004')

payload = {
    'comment': 'IBAM2001: other has packed 2 of WH/PACK/13766<br>Items: DW-K-ARMS-SB05-44-BLK-M16R-JZS160 (x1) | DW-K-ARMS-SB05-44-BLK-M16R-IS200 (x1.0) | STANCE-K-CUPOPTION-12-5 (x0)<br>Tracking Number: 1ZXXXXXXXXXXXXXXXX',
    'complete': False,
    'items': [
        {'product_id': 31345, 'qty_done': 1},
        {'product_id': 139, 'qty_done': 2},
        {'product_id': 31345, 'qty_done': 1},
        {'product_id': 139, 'qty_done': 2},
        {'product_id': 6608, 'qty_done': 0}
    ]
}
# https://dw-uat.glodo.cloud//dwapi/v1/orders/S125999/pack