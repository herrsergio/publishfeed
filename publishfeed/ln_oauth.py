#!/usr/bin/env python
'''
Simple Authentication script to log-on the Linkedin API

@author:    Jean-Christophe Chouinard.
@role:      Sr. SEO Specialist at SEEK.com.au
@website:   jcchouinard.com
@LinkedIn:  linkedin.com/in/jeanchristophechouinard/
@Twitter:   twitter.com/@ChouinardJC
'''
import json
import random
import requests
import string


def ln_auth(credentials):
    '''
    Run the Authentication.
    If the access token exists, it will use it to skip browser auth.
    If not, it will open the browser for you to authenticate.
    You will have to manually paste the redirect URI in the prompt.
    '''
    creds = ln_read_creds(credentials)
    #print(creds)
    client_id, client_secret = creds['client_id'], creds['client_secret']
    redirect_uri = creds['redirect_uri']
    api_url = 'https://www.linkedin.com/oauth/v2'

    if 'access_token' not in creds.keys():
        args = client_id, client_secret, redirect_uri
        auth_code = ln_authorize(api_url, *args)
        access_token = ln_refresh_token(auth_code, *args)
        creds.update({'access_token': access_token})
        ln_save_token(credentials, creds)
    else:
        access_token = creds['access_token']
    return access_token


def ln_headers(access_token):
    '''
    Make the headers to attach to the API call.
    '''
    headers = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': 'no-cache',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    return headers


def ln_read_creds(filename):
    '''
    Store API credentials in a safe place.
    If you use Git, make sure to add the file to .gitignore
    '''
    with open(filename) as f:
        credentials = json.load(f)
    return credentials


def ln_save_token(filename, data):
    '''
    Write token to credentials file.
    '''
    data = json.dumps(data, indent=4)
    with open(filename, 'w') as f:
        f.write(data)


def ln_create_CSRF_token():
    '''
    This function generate a random string of letters.
    It is not required by the Linkedin API to use a CSRF token.
    However, it is recommended to protect against cross-site request forgery
    For more info on CSRF https://en.wikipedia.org/wiki/Cross-site_request_forgery
    '''
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token


def ln_open_url(url):
    '''
    Function to Open URL.
    Used to open the authorization link
    '''
    import webbrowser
    print(url)
    webbrowser.open(url)


def ln_parse_redirect_uri(redirect_response):
    '''
    Parse redirect response into components.
    Extract the authorized token from the redirect uri.
    '''
    from urllib.parse import urlparse, parse_qs

    url = urlparse(redirect_response)
    url = parse_qs(url.query)
    return url['code'][0]


def ln_authorize(api_url, client_id, client_secret, redirect_uri):
    # Request authentication URL
    csrf_token = ln_create_CSRF_token()
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': csrf_token,
        'scope': 'r_liteprofile,r_emailaddress,w_member_social'
    }

    response = requests.get(f'{api_url}/authorization', params=params)

    print(f'''
    The Browser will open to ask you to authorize the credentials.\n
    Since we have not setted up a server, you will get the error:\n
    This site can't be reached. localhost refused to connect.\n
    This is normal.\n
    You need to copy the URL where you are being redirected to.\n
    ''')

    ln_open_url(response.url)

    # Get the authorization verifier code from the callback url
    redirect_response = input('Paste the full redirect URL here:')
    auth_code = ln_parse_redirect_uri(redirect_response)
    return auth_code


def ln_refresh_token(auth_code, client_id, client_secret, redirect_uri):
    '''
    Exchange a Refresh Token for a New Access Token.
    '''
    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(access_token_url, data=data, timeout=30)
    response = response.json()
    #print(response)
    access_token = response['access_token']
    return access_token


if __name__ == '__main__':
    credentials = '/home/ubuntu/publishfeed/publishfeed/ln_credentials.json'
    access_token = ln_auth(credentials)
