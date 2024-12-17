import socket
import json
from app.models import Printers
from sqlalchemy import and_





def send_zpl_to_server(server_name, printer_name, zpl_data):
    try:
        # Prepare the JSON payload
        payload = {
            "printer": printer_name,
            "zpl_data": zpl_data
        }

        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port=9100 # this will always be this
            s.connect((server_name, port))
            s.sendall(json.dumps(payload).encode())
        return {'state':'Success', 'value':'This value is unused'}

    except Exception as e:
        return {'state':'Error', 'value':e}





def find_printer(printer_loc, label_size):
    # first find the can print filter
    if label_size == '4x6':
        can_print_filter = Printers.can_print_4x6
    elif label_size == '4x675':
        can_print_filter = Printers.can_print_4x675

    # query the table for results and grab the first row that satisfies these conditions
    results = Printers.query.filter(
        and_(
            Printers.printer_loc == printer_loc,
            can_print_filter == True
        )
    ).with_entities(Printers.server_name, Printers.printer_name).first()

    # parse the results
    if not results:
        return {'state':'Error', 'value':f'No printer could be found that can print {label_size} in {printer_loc}'}
    else:
        return {'state':'Success', 'value':results}