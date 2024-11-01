import logging
import random
import time

from flask import Flask

app = Flask(__name__)


@app.route('/')
def logger():
    limit = 10
    count = 0
    while True:
        logging.info(f"INFO: Random Number Generated: {random.randint(0, 100)}")
        time.sleep(60)
        count += 1
        if count == limit:
            return f'Logging ran {limit} times'


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
