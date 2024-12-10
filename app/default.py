from flask import Blueprint, render_template, session, redirect, request

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





"""
For ClickUp auth redirects
"""
@default.route('/clickup_callback')
def clickup_callback():
    # Get the authorization code from the request
    code = request.args.get('code')
    print(code)
    # if not code:
    #     return "Authorization code not found", 400

    # # Exchange the authorization code for an access token
    # token_url = "https://app.clickup.com/api/v2/oauth/token"
    # data = {
    #     'client_id': CLIENT_ID,
    #     'client_secret': CLIENT_SECRET,
    #     'code': code,
    #     'redirect_uri': REDIRECT_URI
    # }
    # response = requests.post(token_url, json=data)
    # if response.status_code == 200:
    #     access_token = response.json().get('access_token')
    #     return jsonify({"access_token": access_token})
    # else:
    #     return f"Failed to get access token: {response.json()}", response.status_code