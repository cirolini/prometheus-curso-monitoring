from flask import Flask
from prometheus_client import Counter, CollectorRegistry, write_to_textfile, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

registry = CollectorRegistry()
c = Counter('requests_total', 'Description of counter', registry=registry)

@app.route('/')
def hello_world():
    c.inc()
    return 'Hello, World!'

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app(registry=registry)
})
