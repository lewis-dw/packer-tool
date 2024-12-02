from flask import Blueprint, render_template, session, redirect

"""
These routes are for default operations on the Website/PWA
"""
default = Blueprint('default', __name__, template_folder='templates/default', static_folder='static')



"""
Loading the main dashboard where user can switch between different options
"""
@default.route('/')
def index():
    return render_template('dashboard.html')





"""
For testing purposes this clears all session data
"""
@default.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()
    return redirect('/')