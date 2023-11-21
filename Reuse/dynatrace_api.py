import json
import os
import random
import requests
import time
import traceback

from functools import partial
from json import JSONDecodeError


class RateLimitException(Exception):
    """Raised when HTTP Status Code 429 indicates rate limiting"""
    pass


# For get only currently, support bypassing cert verification
verify_certificate = os.getenv('DYNATRACE_API_VERIFY_CERTIFICATE', 'true')
if verify_certificate.lower() == 'false':
    verify_certificate = False
    print('WARNING: Certificate verification is being bypassed (for gets only)')
    requests.packages.urllib3.disable_warnings()
else:
    verify_certificate = True


def get(url, token, endpoint, params):
    # For debugging pagination
    # page_number = 1

    # Allow for rare cases of passing the complete endpoint as a URL in addition to the common case of passing the relative path of the endpoint
    # For the very special (and untested) case of calling ActiveGate endpoints over port 9999, do not verify the certificate
    verify = verify_certificate

    if endpoint.startswith('https://'):
        full_url = endpoint
        if ':9999' in endpoint:
            verify = False
            requests.packages.urllib3.disable_warnings()
    else:
        full_url = url + endpoint

    fn = partial(rate_limited_get, full_url, params=params, headers={'Authorization': "Api-Token " + token}, timeout=60.0, verify=verify)
    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'GET Failed for URL "{full_url}" with parameters "{params}"')
        raise SystemExit(e)

    try:
        json_data = r.json()
    except JSONDecodeError as e:
        handle_exception(e, f'JSON decode error. Response Text: {r.text}')
        raise SystemExit(e)

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        # For debugging pagination
        # page_number += 1
        # print(f'Getting page number {page_number} with next page key of "{next_page_key}"')
        params = {'nextPageKey': next_page_key}
        full_url = url + endpoint
        fn = partial(rate_limited_get, full_url, params=params, headers={'Authorization': "Api-Token " + token}, timeout=60.0, verify=verify)
        try:
            r = retry_with_backoff(fn)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            handle_exception(e, f'Paginated GET Failed with {r.status_code} - {r.reason} {r.text}. URL: {full_url}. Params: {params}')
            raise SystemExit(e)

        json_data = r.json()

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def get_object_list(env, token, endpoint):
    url = env + endpoint
    return get_without_pagination(url, token)


def get_plain_text_list(env, token, endpoint):
    url = env + endpoint
    return get_without_pagination(url, token)


def get_by_object_id(env, token, endpoint, object_id):
    url = env + endpoint + '/' + object_id
    r = get_without_pagination(url, token)
    return json.loads(r.text)


def get_without_pagination(url, token):
    """get with rate limit and connection exception exponential backoff, but without pagination support"""
    fn = partial(rate_limited_get, url, params='', headers={'Authorization': "Api-Token " + token}, timeout=60.0, verify=verify_certificate)
    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'Failed to get url "{url}"')
        raise SystemExit(e)

    return r


def post(env, token, endpoint, payload):
    # In general, avoid post in favor of put so "fixed ids" can be used
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    fn = partial(rate_limited_post, url, formatted_payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'}, timeout=60.0, verify=verify_certificate)
    try:
        r = retry_with_backoff(fn)
        if r.status_code not in [200, 201, 204]:
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                try:
                    name = json_data.get('name')
                    if name:
                        print('Name: ' + name)
                except AttributeError:
                    print(formatted_payload)
                print('Error in "dynatrace_api.post(env, token, endpoint: str, payload: str)" method')
                print('See ' + error_filename + ' for more details')
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'Failed to put to endpoint "{endpoint}" for payload "{payload}"')
        raise SystemExit(e)

    return r


def post_plain_text(env, token, endpoint, payload):
    url = env + endpoint

    fn = partial(rate_limited_post, url, payload, headers={'Authorization': 'Api-Token ' + token, 'accept':  '*/*', 'Content-Type': 'text/plain; charset=utf-8'}, timeout=60.0, verify=verify_certificate)
    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'Failed to post plain text to endpoint "{endpoint}" for payload "{payload}"')
        raise SystemExit(e)

    return r


def put(env, token, endpoint, object_id, payload):
    # In general, favor put over post so "fixed ids" can be used
    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    if object_id:
        url = env + endpoint + '/' + object_id
    else:
        url = env + endpoint

    fn = partial(rate_limited_put, url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'}, timeout=60.0, verify=verify_certificate)
    try:
        r = retry_with_backoff(fn)
        if r.status_code not in [200, 201, 204]:
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(json_data)
                print('Error in "dynatrace_api.put(env, token, endpoint, object_id, payload)" method')
                print('See ' + error_filename + ' for more details')
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'Failed to put to endpoint "{endpoint}" for payload "{payload}"')
        raise SystemExit(e)

    return r


def put_without_id(env, token, endpoint, payload):
    return put(env, token, endpoint, None, payload)


def delete(env, token, endpoint, object_id):
    url = f'{env}{endpoint}/{object_id}'

    fn = partial(rate_limited_delete, url, headers={'Authorization': "Api-Token " + token}, timeout=60.0, verify=verify_certificate)
    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        handle_exception(e, f'Failed to delete object id "{object_id}" from endpoint "{endpoint}"')
        raise SystemExit(e)

    return r


def rate_limited_get(url, params, headers, timeout, verify):
    r = requests.get(url, params, headers=headers, timeout=timeout, verify=verify)
    if r.status_code == 429:
        print('Rate limiting in effect.  Performing exponential backoff retries.')
        raise RateLimitException
    return r


def rate_limited_delete(url, headers, timeout, verify):
    r = requests.delete(url, headers=headers, timeout=timeout, verify=verify)
    if r.status_code == 429:
        print('Rate limiting in effect.  Performing exponential backoff retries.')
        raise RateLimitException
    return r


def rate_limited_post(url, payload, headers, timeout, verify):
    r = requests.post(url, payload, headers=headers, timeout=timeout, verify=verify)
    if r.status_code == 429:
        print('Rate limiting in effect.  Performing exponential backoff retries.')
        raise RateLimitException
    return r


def rate_limited_put(url, payload, headers, timeout, verify):
    r = requests.put(url, payload, headers=headers, timeout=timeout, verify=verify)
    if r.status_code == 429:
        print('Rate limiting in effect.  Performing exponential backoff retries.')
        raise RateLimitException
    return r


def retry_with_backoff(fn, retries=5, backoff_in_seconds=1):
    """Simple exponential backoff implementation from https://keestalkstech.com/2021/03/python-utility-function-retry-with-exponential-backoff/
    with minor modifications (specify exceptions handled, modified formatting)"""
    x = 0
    while True:
        try:
            return fn()
        except (ConnectionError, TimeoutError, RateLimitException):
            if x == retries:
                raise

            sleep = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
            time.sleep(sleep)
            x += 1


# Wrapper for requests that converts HTTP Status Code 429 to RateLimitException
def handle_exception(e, message):
    print(message)
    if isinstance(e, requests.exceptions.RequestException):
        if e.response.text:
            print("Please check the following HTTP response to troubleshoot the issue:")
            print(e.response.text)
    print("Exiting Program")
    traceback.print_exc()
