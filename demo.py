#!/usr/bin/env python3.7

"""./demo.py, then point your browser at localhost:5000/web

Note that this demo uses a fairly simple implementation of login, as the goal
is to demo the CSRF functionality, not the session management.  Your
implementation might be using OAuth rather than cookie-based logins, and that
is fine.  As long as your session management generates a unique, ephemeral
identity (such as a session id or an OAuth bearer token), code similar
to this demo should work.

There are two types of pages returned from this demo.  We return JSON
from the /api/ urls and we return web pages from the /web/ urls.  The
/api/ JSON is handled by the flask-restplus-csrf api object. The /web/ 
urls are handled by the traditional flask App.  We return the CSRF 
token for API calls that themselves require the token.  We add the
CSRF token to all /web/ pages if the user is logged in.

The /web/ urls get the token added to the head of the document.  If
you look in the template, you'll see that pages call csrf.js, which
then adds the token to any forms in the web page.  If you dynamically
generate your forms, you will have to manually call addTokenToForms
after those forms are in the DOM.

See the test_demo.py file for some examples of how to access these APIs.

"""

import xml.etree.ElementTree as etree
from flask import Flask, render_template, request, session
from flask_restplus import Resource, Api, utils
import os
import time

## This is a mock of user storage.  We store username and passphrase
STORAGE = {
    "admin": {'pass':'secret'},
    "james": {'pass':'foosball'}
}

app = Flask(__name__)
app.debug = True

# The app secret key is used to digitally sign the session cookie.  This is why
# we can rely on session['logged_in'] = True as our login flag.  Here we
# generate the key randomly, but note that means it does not persist past
# restarts of the server.
app.secret_key = os.urandom(32)  # 256-bit random encryption key

## We call Api with a csrf=True parameter.  We could alternatively pass
## a csrf instance (subclassed or otherwise) as the value of parameter
## csrf.  This would allow us to, for example, change how usernames
## are stored by overriding get_username.  See csrf.py for more.
api = Api(app, csrf=True)

# CSRF requests should not be done via GET, so we disable GET for some
# functions via this subclass of Resource
class ForcePost(Resource):
    def get(self):
        return {'message': 'Resource only available via POST. Please try again.'}

def do_logout():
    # Clear session info from cookie
    session.pop('logged_in', None)
    session.pop('username', None)

    # Destroy the CSRF session id
    api.csrfHandler.logout()
    
def process_login():
    ## We've just mocked up a storage implementation as an in-memory dict.
    ## Replace this with your actual storage solution for usernames and
    ## passwords.
    username = request.values.get('username', '')
    if (not username in STORAGE.keys()
        or request.values.get('passphrase', '') != STORAGE[username]['pass']):

        do_logout()
        return False

    # User has provided correct credentials
    session['logged_in'] = True
    session['username'] = username
    return True
    
# This just tells us if we're logged in
@api.route('/api/logged_in')
class LoggedInApiHandler(Resource):
    def get(self):
        return {'message': session.get('logged_in', False)}

# This just tells us if we have a valid token
@api.route('/api/token_valid')
class TokenApiHandler(ForcePost):
    def post(self):
        if not session.get('logged_in', False):
            ret = {'message': False}
            return ret, 403

        username = session.get('username', '')
        if not username:
            # Shouldn't be possible to get here, but just in case
            ret = {'message': False}
            return ret, 403

        valid = api.csrfHandler.token_valid(request.values.get('csrf', ''), username)
        ret = {'message': valid}
        return ret

@api.route('/api/secured_endpoint')
class SecuredEndpoint(ForcePost):
    @api.csrf
    def post(self):
        return {'message': 'Secret information'}

@api.route('/api/insecured_endpoint')
class SecuredEndpoint(Resource):
    def get(self):
        return self.post()
    def post(self):
        return {'message': 'NON secret information'}

@api.route('/api/login')
class LoginHandler(Resource):
    def get(self):
        if process_login():
            ret = {
                'message': 'Login success',
                'csrf':api.csrfHandler.generate_token()
            }
            return ret
        else:
            return {'message':'Login fail'}, 401

@api.route('/api/logout')
class LogoutHandler(Resource):
    def get(self):
        do_logout()
        return {'message':'Logout success'}

@app.route('/web', methods=['GET'])
def homeHandler():
    ctx = {
        'session':session,
    }
    return render_template('home.html', **ctx)

@app.route('/web/login', methods=['POST'])
def loginWebHandler():
    ctx = {
        'session':session,
    }
    
    if process_login():
        ctx['message'] = "Login Success"
    else:
        ctx['message'] = "Login Fail"
        
    return render_template('home.html', **ctx)

@app.route('/web/logout', methods=['GET'])
def logoutWebHandler():
    do_logout()
    return homeHandler()

@app.route('/web/insecure', methods=['GET', 'POST'])
def web_secure_handler():
    return "<html><body>NON secure information.</body></html>"

@app.route('/web/secure', methods=['GET', 'POST'])
@api.csrf
def web_secure_handler():
    return "<html><body>Secure information.</body></html>"


## This function is run after every request for a page in /web/, but
## not in calls to the /api/ urls.  It adds the csrf token to the
## head.
@app.after_request
def add_token(response):
    """Add token to web pages if we're logged in."""
    
    # If there's no csrf handler, we're not doing csrf, so no need to
    # add a token at all.
    if not api.csrfHandler:
        return response
    
    # If we're not logged in, don't add the token
    if not api.csrfHandler.logged_in():
        return response

    return api.csrfHandler.add_token_to_html(response)

if __name__ == '__main__':
    app.run(debug=True)
