from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'HELLO'


@app.route('/1')
def route1():
    return 'Route 1'


@app.route('/2')
def route2():
    return 'Route 2'


@app.route('/3')
def route3():
    return 'Route 3'


if __name__ == '__main__':
    app.run()