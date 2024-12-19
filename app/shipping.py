from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from flask import Blueprint, request, redirect, render_template, url_for, session, current_app, send_file
from app.shipper import shipping_functions
from app.print_zpl import printer
from app.parcel_packer import packer
from app.logger import update_log
from app import fedex, ups
from io import BytesIO
from datetime import datetime
from app.models import ShippingHistory, Labels, Printers


"""
These routes are used for quoting and shipping an order
"""
shipping = Blueprint('shipping', __name__, template_folder='templates/shipping', static_folder='static')





"""
Preprocess some parcel values here then display them to user and allow them to edit/add/remove the parcels
"""
@shipping.route('/create_parcels')
def create_parcels():
    # get the currently loaded data from flask session
    data = session.get('order_data', {})

    # if there is data then calculate parcels if they dont exist yet, if they do just load them in
    if data:
        parcels = data.get('parcels', '')
        if not parcels:
            # parcels = packer.calculate_parcels(data['commercial_invoice_lines'])
            parcels = packer.temp_parcels() # temporary

            # update the order data
            session['order_data']['parcels'] = parcels
            session.modified = True
        return render_template('show_parcels.html', parcels=parcels)


    # else just redirect them back to the homepage they shouldnt be here
    else:
        return redirect('/')


@shipping.route('/get_parcels', methods=['POST'])
def get_parcels():
    # parse over the form
    parcels = packer.parse_form(request.form)

    # assign the parcels back to the order data and redirect
    session['order_data']['parcels'] = parcels
    session.modified = True
    return redirect(url_for('shipping.quote_result'))





"""
Quote the data with every courier
"""
def run_with_app_context(app, func, *args, **kwargs):
    """
    Helper to execute a threaded function with the Flask app context.
    """
    with app.app_context():
        return func(*args, **kwargs)

@shipping.route('/quote_result')
def quote_result():
    # get the currently loaded data from flask session
    data = session.get('order_data', {})
    shipper = request.cookies.get('current_shipper')


    # if there is data then proceed
    if data:
        # need to make a copy of data where sat indicator is false so we can see those values too
        # if sat indicator is already not there so we dont need to create a no sat quote
        if data['sat_indicator'] == '':
            do_no_sat = False

        # if sat indicator isnt already there then create a no sat quote as well
        else:
            do_no_sat = True
            no_sat_data = data.copy()
            no_sat_data['sat_indicator'] = ''

        # after verification proceed to quote the order using concurrent futures
        update_log.create_log_line('actions', f"`{shipper}` attempting to quote {data['order_name']} to {data['shipping_country']} ({data['shipping_country_id']}).")
        all_quotes = []
        all_errors = []

        cur_app = current_app._get_current_object()
        with ThreadPoolExecutor() as executor:
            # create the futures to commit map
            services = [
                (fedex.quote_order, deepcopy(data), 'FedEx'),
                (ups.quote_order, deepcopy(data), 'UPS'),
                (ups.quote_order, deepcopy(no_sat_data), 'UPS - No SAT') if do_no_sat else None
            ]
            services = list(filter(None, services))

            # submit the futures
            future_to_service = {}
            for service, data_copy, service_name in services:
                future_to_service[executor.submit(run_with_app_context, cur_app, service, data_copy)] = service_name


            # process results as they complete
            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                update_log.create_log_line('results', f'{service_name} has completed.')
                quote = future.result()
                if quote['state'] == 'Success':
                    all_quotes.extend(quote['value'])
                else:
                    all_errors.extend(quote['value'])


        # log the quoting results
        update_log.create_log_line('actions', f'{len(all_quotes)} valid. {len(all_errors)} errors.')
        update_log.create_log_line('results', f'Successful quotes: {len(all_quotes)}')
        update_log.create_log_line('results', f'Errors: {all_errors}')


        # parse the quote results then display to the user
        quote_content, error_content = shipping_functions.parse_quotes({'quotes':all_quotes, 'errors':all_errors})
        data = {
            'order_id': data['order_name'],
            'country_to': data['shipping_country'],
            'quote_content': quote_content,
            'error_content': error_content
        }

        return render_template('quote_result.html', data=data)

    # else just redirect them back to the homepage they shouldnt be here
    else:
        return redirect('/')





"""
This page handles the user selecting a shipping method from the quote page
"""
@shipping.route('/select_method')
def select_method():
    # get the args and set vars
    data = session.get('order_data', {})
    courier = request.args.get('courier').upper()
    shipping_code = request.args.get('shipping_code')
    sat_indicator = request.args.get('sat_indicator')
    dw_paid = request.args.get('cost')
    printer_loc = request.args.get('printer_loc')
    shipper = request.cookies.get('current_shipper')


    # only proceed if there is currently data
    if data:
        if shipper:
            # log the action
            sat_msg = 'Yes' if sat_indicator else 'No'
            update_log.create_log_line('actions', f'`{shipper}` attempting to ship with {courier} using {shipping_code}, SAT: {sat_msg}.')


            # try find a printer that can print what the user selected
            res = Printers.find_printer(printer_loc, courier)

            # parse results
            if res['state'] == 'Success':
                server_name, printer_name, label_size = res['value']
                changed_printer = ''
            else:
                server_name = 'LOGISTICS'
                printer_name = 'wifizebra'
                label_size = '4x6'
                changed_printer = f"{res['value']}, switched to `wifizebra` in Josh Area."



            """Ship the order based on who was selected"""
            # ups
            if courier == 'UPS':
                result, ship_at = ups.ship_order(data, shipping_code, sat_indicator)

            # fedex
            elif courier == 'FEDEX':
                result, ship_at = fedex.ship_order(data, shipping_code, label_size)


        # if they access with no shipper selected then redirect to a page telling them this
        else:
            update_log.create_log_line('actions', f'No shipper selected redirecting them to a selection page.')
            return render_template('no_shipper.html')

    # if they access the page with no data redirect them back to the dashboard
    else:
        return redirect('/')


    # deal with result of a successful ship and log a message respective of what happened
    if result['state'] == 'Error':
        errors = result['value']
        ship_result = f'Failed with {courier}. Error/s: {errors}'
    else:
        master_id = result['value']['master_id']
        labels = result['value']['labels']
        commercial_invoice = result['value'].get('commercial_invoice', None)
        ship_result = f'Successfully shipped with {courier}. Tracking number: {master_id}'

    # log all that has happened
    update_log.create_log_line('actions', result['state'])
    update_log.create_log_line('results', ship_result)
    update_log.create_log_line('results', changed_printer)


    # if success then we need need to do other stuff
    if result['state'] == 'Success':
        # update the outs table in database
        ShippingHistory.add_row(data['order_name'], shipper, datetime.now(), ship_at, data['shipping_name'], data['shipping_company'], data['shipping_country_id'], data['shipping_cost'], float(dw_paid), master_id, courier, shipping_code, commercial_invoice)

        # loop over labels
        label_results = []
        for label_id, label_dict in enumerate(labels):
            # send the zpl data to the print server
            # server_name and printer_name were found earlier
            # print_res = printer.send_zpl_to_server(server_name, printer_name, label_dict['label_data'])
            print_res = {
                'state': 'Success'
            }

            # deal with result of printing the label
            initial_message = f'Label {label_id+1}/{len(labels)} for {master_id}'
            if print_res['state'] == 'Error':
                print_result = f"{initial_message} failed to print. Reason: {print_res['value']}"
            else:
                print_result = f'{initial_message} succeeded printing to {printer_name} in {printer.friendly_translate(printer_loc)}'
            update_log.create_log_line('results', print_result)

            # create result info dict for the row
            label_results.append({
                'label_id': label_dict['label_name'],
                'changed_printer': changed_printer,
                'print_result': print_result
            })

            # update the labels table
            Labels.add_row(data['order_name'], master_id, label_dict['label_name'], label_dict['label_data'], courier, shipping_code)


    # render the results to the user
    return render_template('ship_result.html', ship_result=ship_result, label_results=label_results)





"""
This page handles the user searching for an order number and selecting which labels from that order to print
"""
@shipping.route('/reprint_label', methods=['GET', 'POST'])
def reprint_label():
    # handle the user searching for order_id
    if request.method == 'GET':
        # search for labels relating to the order id passed in
        order_id = request.args.get('order_id', '')
        result = Labels.get_labels_for_order(order_id)

        # parse the result
        if result['state'] == 'Success':
            return render_template('reprint_label.html', order_id=order_id, labels=result['value'])
        else:
            return render_template('bad_search.html', message=result['value'], _from='reprint_label')


    # handle the user's selections to reprint
    elif request.method == 'POST':
        for key, _ in request.form.items():
            # get the zpl data from the label id and send a print request to the print server
            zpl_data = Labels.get_zpl_data(key)
            res = printer.send_zpl_to_server('LOGISTICS', 'UPS', zpl_data)
            if res['state'] == 'Error':
                update_log.create_log_line('results', res['value'])
        return redirect('/')


    # not sure how the user would trigger this but we need to catch it before we continue
    else:
        return redirect('/')





"""
This page handles the user searching for an order number and selecting which labels from that order to print
"""
@shipping.route('/get_invoice', methods=['GET', 'POST'])
def get_invoice():
    # handle the user searching for order_id
    if request.method == 'GET':
        # get the order id from the query and search for it
        order_id = request.args.get('order_id', '')
        result = ShippingHistory.search_for_invoice(order_id)

        # parse the result
        if result['state'] == 'Success':
            return render_template('get_invoice.html', order_id=order_id, results=result['value'])
        else:
            return render_template('bad_search.html', message=result['value'], _from='get_invoice')


    # handle the user's selection to download
    elif request.method == 'POST':
        # get the commercial invoice by row id
        row_id = request.form.get('row_id')
        action = request.form.get('action')
        order_name, commercial_invoice = ShippingHistory.search_row_id(row_id)

        # wrap the pdf data in a BytesIO object
        pdf_data = BytesIO(commercial_invoice)


        # serve the file based on the action
        if action == 'view':
            # use inline content-disposition to open in a browser tab
            response = send_file(
                pdf_data,
                mimetype='application/pdf'
            )
            response.headers['Content-Disposition'] = f'inline; filename="commercial_invoice_{order_name}.pdf"'
            return response

        elif action == 'download':
            # use attachment content-disposition to trigger a direct download
            return send_file(
                pdf_data,
                download_name=f'commercial_invoice_{order_name}.pdf', # give the file a name
                mimetype='application/pdf',
                as_attachment=True
            )


    # not sure how the user would trigger this but we need to catch it before we continue
    else:
        return redirect('/')





"""
This page displays all the shipping history
"""
@shipping.route('/shipping_history')
def shipping_history():
    history_result = ShippingHistory.get_shipping_history()
    return render_template('shipping_history.html', history=history_result)