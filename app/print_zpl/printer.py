import socket
import json



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
        try:
            # send the zpl payload
            port=9100 # this will always be the port of the print server
            s.connect((server_name, port))
            s.send(payload)

            # receive the response from the print server
            res = json.loads(
                s.recv(4096).decode()
            )

        # catch failed connection error
        except socket.gaierror as e:
            res = e

        # finally close the socket regardless of what occurred
        finally:
            s.close()

    return res