from flask import Flask
from prometheus_client import Counter, CollectorRegistry, write_to_textfile

app = Flask(__name__)

registry = CollectorRegistry()
c = Counter('requests_total', 'Description of counter', registry=registry)

@app.route('/metrics')
def prometheus_metrics():
    write_to_textfile('app.prom', registry)
    return 'metrics write'

@app.route('/')
def hello_world():
    c.inc()
    return 'Hello, World!'
