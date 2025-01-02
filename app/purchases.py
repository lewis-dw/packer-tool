import re
from flask import Blueprint, request, redirect, render_template, url_for, session, send_file
from app.odoo.api import parse_product_description


"""
These routes are used for quoting and shipping an order
"""
purchasing = Blueprint('purchases', __name__, template_folder='templates/purchasing', static_folder='static')



@purchasing.route('/temp_tool', methods = ['POST', 'GET'])
def temp_tool():
    result = ''
    text = ''
    if request.method == 'POST':
        text = request.form.get('text')
        parsed_text = parse_product_description(text)

        result = []
        for option in parsed_text:
            option = re.sub(r'<.*?>', ' ', option)
            option = re.sub(' +', ' ', option).strip()
            result.append(option)
        result = '\n'.join(result)
    return render_template('temp.html', text=text, result=result)