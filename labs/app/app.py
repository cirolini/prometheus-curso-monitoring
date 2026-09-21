"""Exporter de exemplo do modulo 05, com um pouco mais de carne.

A ideia e' a mesma da licao: uma aplicacao Flask minima que expoe as
proprias metricas em /metrics. A diferenca e' que aqui ela ja nasce
com os quatro tipos de metrica do modulo 03, para dar o que consultar
no Prometheus e o que desenhar no Grafana.
"""
import random
import time

from flask import Flask
from prometheus_client import Counter, Gauge, Histogram, Summary, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Counter: so sobe. Zera quando a aplicacao reinicia.
requests_total = Counter(
    "app_requests_total",
    "Total de requisicoes recebidas pela aplicacao",
    ["endpoint", "status"],
)

# Gauge: sobe e desce.
inflight = Gauge(
    "app_requests_inflight",
    "Requisicoes sendo atendidas neste instante",
)

app_version = Gauge(
    "app_build_info",
    "Metadado da build. O valor e' sempre 1; o que importa sao os labels.",
    ["version"],
)
app_version.labels(version="2.0.0").set(1)

# Histogram: buckets. E' com ele que se calcula percentil no servidor,
# com histogram_quantile(). Prefira histogram a summary.
latency = Histogram(
    "app_request_duration_seconds",
    "Duracao das requisicoes",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# Summary: quantis calculados no cliente. Esta aqui para efeito de
# comparacao com o histogram - na pratica, prefira o histogram.
payload = Summary(
    "app_payload_bytes",
    "Tamanho do payload devolvido",
)


@app.route("/")
def hello_world():
    with inflight.track_inprogress():
        start = time.perf_counter()
        time.sleep(random.expovariate(20))  # latencia sintetica
        body = "Hello, World!" * random.randint(1, 20)
        latency.labels(endpoint="/").observe(time.perf_counter() - start)
        payload.observe(len(body))
        requests_total.labels(endpoint="/", status="200").inc()
        return body


@app.route("/erro")
def erro():
    """Rota para gerar erro de proposito e ver o alerta/grafico reagir."""
    with inflight.track_inprogress():
        start = time.perf_counter()
        time.sleep(random.expovariate(10))
        latency.labels(endpoint="/erro").observe(time.perf_counter() - start)
        requests_total.labels(endpoint="/erro", status="500").inc()
        return "boom", 500


@app.route("/health")
def health():
    return "ok"


# Expoe /metrics ao lado da aplicacao, sem precisar de uwsgi.
# A licao antiga mandava instalar uwsgi, que compila e costuma falhar
# em Python novo. Isto aqui resolve o mesmo problema sem dor.
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
