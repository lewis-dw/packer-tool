from flask import Blueprint, render_template

"""
These routes are for default operations on the Website/PWA
"""
default = Blueprint('default', __name__, template_folder='templates/default')



"""
Loading the main dashboard where user can switch between different options
"""
@default.route('/')
def index():
    return render_template('dashboard.html')