from flask import Blueprint, render_template, session, redirect, request, make_response
from app.logger import update_log

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
This clears all session data and cookies
"""
@default.route('/clear_session', methods=['POST'])
def clear_session():
    # clear session data
    session.clear()

    # clear cookies
    response = make_response(redirect("/"))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', max_age=0)
    return response




"""
Allows user to switch user roles
"""
@default.route('/switch_role', methods=['POST'])
def switch_role():
    new_role = request.form.get('user-role')
    print(new_role)
    return redirect('/')



"""
For logging stuff via the js
"""
@default.route('/log_event', methods=['POST'])
def log_event():
    data = request.get_json()
    if data:
        # log the data received
        update_log.create_log_line(data['location'], data['event'])
        return '', 204
    return 'Missing data', 400




"""
Test
"""
@default.route('/test')
def test():
    return render_template('test.html')