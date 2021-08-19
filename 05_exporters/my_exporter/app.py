from flask import Flask
from prometheus_client import Counter, Gauge, CollectorRegistry, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

registry = CollectorRegistry()
c = Counter('requests_total', 'Description of counter', registry=registry)
app_version = Gauge('my_app_version', 'Description of gauge', registry=registry)
app_version.set(1.1)

@app.route('/')
def hello_world():
    c.inc()
    return 'Hello, World!'

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app(registry=registry)
})
