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


default_timeout = 60
default_handle_exceptions = True
default_exit_on_exception = True

# Allows for bypassing certificate verification
default_verify = os.getenv('DYNATRACE_API_VERIFY_CERTIFICATE', 'true')
if default_verify.lower() == 'false':
    default_verify = False
else:
    default_verify = True
default_disable_certificate_warnings = False


def get(env, token, endpoint, params):
    """ Deprecated: Use "get_json_list_with_pagination" instead """
    return get_json_list(f'{env}{endpoint}', token, params=params)


def get_json_list(url, token, params):
    """ Deprecated: Use "get_json_list_with_pagination" instead """
    """ Get a paginated list of JSON objects with default timeout and certificate verification settings """
    return get_json_list_with_pagination(url, token, params=params, timeout=default_timeout, verify=default_verify, disable_verify_warnings=default_disable_certificate_warnings)


def get_json_list_with_pagination(url, token, **kwargs):
    """
    get json list with pagination.
    Called by convenience methods or externally if control is needed.
    Supported keyword arguments:
    params
    headers
    timeout
    verify
    disable_verify_warnings
    handle_exceptions
    exit_on_exception
    """

    # For debugging pagination
    # page_number = 1

    params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception = process_kwargs(token, **kwargs)

    if not verify and disable_verify_warnings:
        requests.packages.urllib3.disable_warnings()

    fn = partial(rate_limited_get, url, params=params, headers=headers, timeout=timeout, verify=verify)

    r = None

    try:
        r = retry_with_backoff(fn)
        # if r.status_code == 404:
        #     print(f'GET for URL "{url}" returned HTTP Status Code 404.  Returning an empty list.')
        #     return []
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        if handle_exceptions:
            handle_exception(e, f'GET Failed for URL "{url}"')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

    json_data = None

    try:
        json_data = r.json()
    except JSONDecodeError as e:
        if handle_exceptions:
            handle_exception(e, f'JSON decode error. Response Text: {r.text}')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

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
        fn = partial(rate_limited_get, url, params=params, headers=headers, timeout=timeout, verify=verify)

        try:
            r = retry_with_backoff(fn)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            if handle_exceptions:
                handle_exception(e, f'Paginated GET Failed with {r.status_code} - {r.reason} {r.text}. URL: {url}. Params: {params}')
                if exit_on_exception:
                    print("Exiting Program")
                    raise SystemExit(e)
            else:
                raise

        try:
            json_data = r.json()
        except JSONDecodeError as e:
            if handle_exceptions:
                handle_exception(e, f'JSON decode error. Response Text: {r.text}')
                if exit_on_exception:
                    print("Exiting Program")
                    raise SystemExit(e)
            else:
                raise

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def get_object_list(env, token, endpoint):
    """ Deprecated: Use "get_without_pagination" instead """
    url = env + endpoint
    return get_without_pagination(url, token)


def get_by_object_id(env, token, endpoint, object_id):
    """ Deprecated: Use "get_without_pagination" instead """
    url = env + endpoint + '/' + object_id
    r = get_without_pagination(url, token)
    return r.json()


def get_without_pagination(url, token, **kwargs):
    """ Get response object without pagination.
    Called by convenience methods or externally if control is needed.
    Supported keyword arguments:
    params
    headers
    timeout
    verify
    disable_verify_warnings
    handle_exceptions
    exit_on_exception
    """

    params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception = process_kwargs(token, **kwargs)

    if not verify and disable_verify_warnings:
        requests.packages.urllib3.disable_warnings()

    fn = partial(rate_limited_get, url, params=params, headers=headers, timeout=timeout, verify=verify)

    r = None

    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        if handle_exceptions:
            handle_exception(e, f'Failed to get URL "{url}"')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

    return r


def post(env, token, endpoint, payload):
    """ Deprecated: Use "post_object" instead """
    return post_object(f'{env}{endpoint}', token, payload)


def post_object(url, token, payload, **kwargs):
    # In general, avoid post in favor of put so "fixed ids" can be used
    params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception = process_kwargs(token, **kwargs)
    # Only use headers if actually passed, since the default is not good for this method
    # TODO: Experiment with using the "JSON" header for all calls except "plain text" ones as new default
    headers = kwargs.get('headers', {'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})

    # print('post_object variables from kwargs:', params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception)
    json_data = None

    if 'application/json' in headers:
        json_data = json.loads(payload)
        formatted_payload = json.dumps(json_data, indent=4, sort_keys=False).encode('utf-8')
    else:
        formatted_payload = payload

    fn = partial(rate_limited_post, url, formatted_payload, headers=headers, timeout=timeout, verify=verify)

    r = None

    try:
        r = retry_with_backoff(fn)
        if r.status_code not in [200, 201, 202, 204]:
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                if 'application/json' in headers:
                    try:
                        name = json_data.get('name')
                        if name:
                            print('Name: ' + name)
                    except AttributeError:
                        print(formatted_payload)
                print('Error in "dynatrace_api.post_object" method')
                print(f'Status Code/Reason: {r.status_code} - {r.reason}')
                print(f'See {error_filename} for payload contents')
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        # print('Requests Exception Handling', handle_exceptions, exit_on_exception)
        if handle_exceptions:
            handle_exception(e, f'Failed to post to URL "{url}" with payload "{payload}"')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

    return r


def post_plain_text(url, token, payload, **kwargs):
    headers = kwargs.get('headers', {'Authorization': 'Api-Token ' + token, 'accept': '*/*', 'Content-Type': 'text/plain; charset=utf-8'})
    kwargs['headers'] = headers
    # print(f'post_plain_text kwargs: {kwargs}')
    return post_object(url, token, payload, **kwargs)


def put_object(url, token, payload, **kwargs):
    # In general, favor put over post so "fixed ids" can be used
    params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception = process_kwargs(token, **kwargs)

    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)

    r = None

    fn = partial(rate_limited_put, url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'}, timeout=60.0, verify=default_verify)
    try:
        r = retry_with_backoff(fn)
        if r.status_code not in [200, 201, 204]:
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(json_data)
                print('Error in "dynatrace_api.put" method')
                print('See ' + error_filename + ' for payload contents')
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        if handle_exception:
            handle_exception(e, f'Failed to put to URL "{url}" for payload "{payload}"')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

    return r


def put(env, token, endpoint, object_id, payload):
    """ Deprecated: Use "put_object" instead """
    if object_id:
        url = env + endpoint + '/' + object_id
    else:
        url = env + endpoint

    return put_object(url, token, payload)


def put_without_id(env, token, endpoint, payload):
    """ Deprecated: Use "put_object" instead """
    return put_object(f'{env}{endpoint}', token, payload)


def delete(env, token, endpoint, object_id):
    """ Deprecated: Use "delete_object" instead """
    return delete_object(f'{env}{endpoint}/{object_id}', token)


def delete_object(url, token, **kwargs):
    params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception = process_kwargs(token, **kwargs)
    if not verify and disable_verify_warnings:
        requests.packages.urllib3.disable_warnings()

    r = None

    fn = partial(rate_limited_delete, url, headers=headers, timeout=timeout, verify=verify)
    try:
        r = retry_with_backoff(fn)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        if handle_exceptions:
            handle_exception(e, f'Failed to delete URL "{url}"')
            if exit_on_exception:
                print("Exiting Program")
                raise SystemExit(e)
        else:
            raise

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
        retry = False
        r = None
        try:
            r = fn()
            if r.status_code == 504:
                print('Retry due to 504: Gateway Timeout')
                retry = True
            if r.status_code == 500 and ('ECONNRESET' in r.text or 'socket hang up' in r.text):
                print(f'Retry due to 500: {r.text}')
                retry = True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ConnectionError, ConnectionResetError, TimeoutError):
            print('Retry due to an exception')
            retry = True

        if retry:
            if x == retries:
                print(f'Retried with exponential backoff {retries} times, but could not recover.')
                raise

            sleep = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
            time.sleep(sleep)
            x += 1
            print(f'Retry number {x} with backoff of {sleep} seconds...')
        else:
            return r


# Wrapper for requests that converts HTTP Status Code 429 to RateLimitException
def handle_exception(e, message):
    print(message)
    if isinstance(e, requests.exceptions.RequestException):
        if e.response.text:
            print("Please check the following HTTP response to troubleshoot the issue:")
            print(e.response.text)
    traceback.print_exc()


def process_kwargs(token, **kwargs):
    default_headers = {'Authorization': "Api-Token " + token}

    params = kwargs.get('params', '')
    headers = kwargs.get('headers', default_headers)
    timeout = kwargs.get('timeout', default_timeout)
    verify = kwargs.get('verify', default_verify)
    disable_verify_warnings = kwargs.get('disable_verify_warnings', default_disable_certificate_warnings)
    handle_exceptions = kwargs.get('handle_exceptions', default_handle_exceptions)
    exit_on_exception = kwargs.get('exit_on_exception', default_exit_on_exception)

    return params, headers, timeout, verify, disable_verify_warnings, handle_exceptions, exit_on_exception


"""
Refactoring Plan:

Pick env or url

get_object_list(env, token, endpoint): SPLIT (returns Response)
get_by_object_id(env, token, endpoint, object_id): SPLIT (returns JSON)
post(env, token, endpoint, payload): SPLIT (returns Response) 
post_plain_text(env, token, endpoint, payload): SPLIT (returns Response)
put(env, token, endpoint, object_id, payload): SPLIT (returns Response)
put_without_id(env, token, endpoint, payload): SPLIT (returns Response)
"""


if __name__ == '__main__':
    print('This module is not designed to be run standalone!')
    print('You might want to run the "Test/Reuse/test_dynatrace_api.py module instead.')
