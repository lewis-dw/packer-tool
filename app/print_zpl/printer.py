import socket
import json
from app.logger import update_log
from app.models import Printers
from sqlalchemy import and_



def friendly_translate(x):
    # need to keep this lookup_dict up to date with:
    # - quote_result.html
    # - printer_info table
    lookup_dict = {
        # label sizes
        '4x675': '4x6.75',

        # locations
        'loc-1': 'main room',
        'loc-2': 'josh area'
    }
    return lookup_dict.get(x, x)





def send_zpl_to_server(server_name, printer_name, zpl_data):
    # serialise the json to a string and convert to bytes for transmission
    payload = json.dumps({
        "printer": printer_name,
        "zpl_data": zpl_data
    }).encode()


    # connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # send the zpl payload
        port=9100 # this will always be this
        s.connect((server_name, port))
        s.send(payload)

        # receive the response from the print server
        res = s.recv(4096).decode()


    # print(res)




    return {'state':'Success', 'value':'This value is unused'}

    # except Exception as e:
    #     return {'state':'Error', 'value':e}





def find_printer(printer_loc, courier):
    # query the table for results and grab the first row that satisfies these conditions
    result = Printers.query.filter(
        and_(
            Printers.printer_loc == printer_loc,
            Printers.can_print.contains(courier.lower())
        )
    ).order_by(Printers.can_print_4x675.desc()).first() # order by if it can print 4x6.75 or not and grab first

    # parse the result
    if result:
        return {'state': 'Success', 'value': (result.server_name, result.printer_name, result.label_size)}
    else:
        return {'state': 'Error', 'value': f'No printer could be found that can print {courier} in {friendly_translate(printer_loc)}'}