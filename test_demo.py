import simplejson as json
import requests
import sys

# Run me with 'pytest test_demo.py'

# Specify a test with 'pytest -k test_foo test_demo.py'

def test_force_post():
    resp = requests.get("http://localhost:5000/api/secured_endpoint")
    assert(resp.status_code == 200)

    data = json.loads(resp.text)
    assert(data['message'] == "Resource only available via POST. Please try again.")

def test_login_fail():
    resp = requests.get("http://localhost:5000/api/login")
    assert(resp.status_code == 401)

    data = json.loads(resp.text)
    assert(data['message'] == "Login fail")

def test_login(session=None):
    if not session:
        session = requests.session()
        
    params = {'username': 'admin', 'passphrase': 'secret'}
    resp = session.get("http://localhost:5000/api/login", params=params)
    assert(resp.status_code == 200)

    data = json.loads(resp.text)
    assert(data['message'] == "Login success")
    assert(data['csrf'])
    
    cookies = resp.cookies
    assert(cookies['session'])

    return resp, data, cookies

def test_logged_in():
    resp = requests.get("http://localhost:5000/api/logged_in")
    assert(resp.status_code == 200)

    data = json.loads(resp.text)
    assert(data['message'] == False)

    # Now login and try again
    resp, data, cookies = test_login()
    session = requests.session()
    resp = session.get("http://localhost:5000/api/logged_in", cookies=cookies)
    data = json.loads(resp.text)
    assert(data['message'] == True)

def test_token_valid():
    # No cookie sent
    session = requests.session()
    resp = session.post("http://localhost:5000/api/token_valid")
    assert(resp.status_code == 403)
    data = json.loads(resp.text)
    assert(data['message'] == False)
    
    # Now, log in and try again
    resp, data, cookies = test_login(session)
    params = {'csrf':data['csrf']}
    print(data)
    resp = session.post("http://localhost:5000/api/token_valid", cookies=cookies,
                        params=params)
    data = json.loads(resp.text)
    print(data)
    assert(data['message'] == True)

    # Now with the wrong cookie
    params = {'csrf':params['csrf']+"wrong"}
    resp = session.post("http://localhost:5000/api/token_valid", cookies=cookies,
                        params=params)
    data = json.loads(resp.text)
    assert(data['message'] == False)
    
def test_csrf_return():
    resp, data, cookies = test_login()
    params = {'csrf':data['csrf']}

    # The logged_in endpoint doesn't require a csrf, but should still return
    # one, since we're logged in.  Let's test it.
    session = requests.session()
    resp = session.get("http://localhost:5000/api/logged_in", cookies=cookies, params=params)
    data = json.loads(resp.text)
    assert('csrf' in data)

def test_logout():
    resp, data, cookies = test_login()
    
    session = requests.session()
    resp = session.get("http://localhost:5000/api/logout", cookies=cookies)
    data = json.loads(resp.text)
    assert(data['message'] == "Logout success")

def test_secured_endpoint():
    # Try without logging in
    session = requests.session()
    resp = session.post("http://localhost:5000/api/secured_endpoint")
    assert(resp.status_code == 403)
    data = json.loads(resp.text)
    assert(data['message'] == 'csrf fail')
    

    # Try logged in
    resp, data, cookies = test_login()
    params = {'csrf':data['csrf']}
    resp = session.post("http://localhost:5000/api/secured_endpoint",
                        cookies=cookies,
                        params=params)
    assert(resp.status_code == 200)
    data = json.loads(resp.text)
    assert(data['message'] == 'Secret information')
