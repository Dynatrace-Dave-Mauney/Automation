# Author: Lucas Roelser <roesler.lucas@gmail.com>
# Modified from serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
# Modified slightly to allow testing with a list of hosts from main

import datetime
import fileinput
import logging
import os
import socket
import ssl
import time


logger = logging.getLogger('SSLVerify')


def ssl_expiry_datetime(hostname: str) -> datetime.datetime:
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    logger.debug('Connect to {}'.format(hostname))
    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    # parse the string from the certificate into a Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)


def ssl_valid_time_remaining(hostname: str) -> datetime.timedelta:
    """Get the number of days left in a cert's lifetime."""
    expires = ssl_expiry_datetime(hostname)
    logger.debug(
        'SSL cert for {} expires at {}'.format(
            hostname, expires.isoformat()
        )
    )
    return expires - datetime.datetime.utcnow()


def test_host(hostname: str, buffer_days: int=30) -> str:
    """Return test message for hostname cert expiration."""
    try:
        will_expire_in = ssl_valid_time_remaining(hostname)
    except ssl.CertificateError as e:
        return f'{hostname} cert error {e}'
    except ssl.SSLError as e:
        return f'{hostname} cert error {e}'
    except socket.timeout as e:
        return f'{hostname} could not connect'
    except ConnectionResetError as e:
        return f'{hostname} connection reset'
    else:
        if will_expire_in < datetime.timedelta(days=0):
            return f'{hostname} cert will expired'
        elif will_expire_in < datetime.timedelta(days=buffer_days):
            return f'{hostname} cert will expire in {will_expire_in}'
        else:
            return f'{hostname} cert is fine'


if __name__ == '__main__':
    loglevel = os.environ.get('LOGLEVEL', 'INFO')
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

    start = time.time()
    host_list = ['google.com', 'dynatrace.com', 'accudraw.labcorp.com']
    for host in host_list:
        host = host.strip()
        logger.debug('Testing host {}'.format(host))
        message = test_host(host)
        print(message)

    logger.debug('Time: {}'.format(time.time() - start))
