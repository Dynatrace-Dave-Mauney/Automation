import json
import requests
import ssl

# Creating an OAuth Client:
# Old UI: Person Icon > Account Settings > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button
# New UI: Person Icon > Account Management > Pick Account if needed > Identity & access management > OAuth Clients > "Create client" button


def get_oauth_bearer_token(client_id, client_secret, scope):
    url = 'https://sso.dynatrace.com/sso/oauth2/token'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }

    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200:
        oauth_bearer_token = json.loads(r.text)['access_token']
        return oauth_bearer_token
    else:
        print(f'POST Request to Get OAuth Bearer Token Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print("Exiting Program")
        exit(1)


def get(oauth_bearer_token, api_url, params):
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    r = requests.get(api_url, headers=headers, params=params)
    if r.status_code == 200:
        # print(r.text)
        return r
    else:
        print(f'GET Request to API URL {api_url} Failed:')
        print(f'Response Status Code: {r.status_code}')
        print(f'Response Reason:      {r.reason}')
        print(f'Response Text:        {r.text}')
        print('Exiting Program')
        exit(1)


def post_multipart_form_data(api_url, files, params, headers):
    try:
        r = requests.post(api_url, files=files, params=params, headers=headers)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
                print('Error in "post_multipart_form_data(api_url, files, params, headers)" method')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "post_multipart_form_data(api_url, files, params, headers)" method')
        raise


def delete(oauth_bearer_token, api_url, params):
    headers = {'accept': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        r = requests.delete(api_url, headers=headers, params=params)
        return r
    except ssl.SSLError:
        print('Error in "new_platform_api.delete(oauth_bearer_token, api_url, object_id)" method')
        print('SSL Error')


def post(oauth_bearer_token, api_url, payload):
    headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + str(oauth_bearer_token)}
    try:
        r = requests.post(api_url, payload, headers=headers)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(payload)
                try:
                    name = payload.get('name')
                    if name:
                        print('Name: ' + name)
                except AttributeError:
                    print(payload)
                print('Error in "new_platform_api.post(oauth_bearer_token, api_url, payload)" method')
                print('See ' + error_filename + ' for more details')
            exit(1)
        return r
    except ssl.SSLError:
        print('Error in "new_platform_api.post(oauth_bearer_token, api_url, payload)" method')
        raise


if __name__ == '__main__':
    print('This module is not designed to be run standalone!')
