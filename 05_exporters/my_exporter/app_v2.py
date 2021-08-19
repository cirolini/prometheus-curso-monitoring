from flask import Flask
app = Flask(__name__)

requests_total = 0

@app.route('/metrics')
def prometheus_metrics():
    return 'app_requests_total {}'.format(requests_total)


@app.route('/')
def hello_world():
    global requests_total
    requests_total += 1
    return 'Hello, World!'
