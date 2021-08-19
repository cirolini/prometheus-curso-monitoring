# Criando seu primeito exporter

Em alguns casos você ja vai ter uma aplicação e quer exportar métricas dela diretamente pela própria aplicação. Aqui vamos desenvolver uma aplicação simples em python usando o Flask que é um minimal framework para desenvolvimento de aplicações web em uma aplicação onde poderemos demonstrar como criar métricas para o prometheus pode ser simples.

## Fase 0; Criando a nossa aplicação

A primeira coisa que precisamos ter é uma aplicação minima. Vamos criar o arquivo app.py.

```
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
```

Para executar essa aplicação vamos criar um virtualenv, `virtualenv env`, e depois ativar o virtualenv, `source env/bin/activate`.

Vamos instalar o flask:

```
pip install flask
```

Agora podemos executar a nossa aplicação com o `flask run`. Se acessarmos um navegador web (http://localhost:5000/) vamos ver as palavras Hello World escritas na tela.

## Fase um: criando uma métrica da forma manual

Existe muitas formas de criar uma métrica para o prometheus poder coletar. Vamos começar de uma forma bem básica, usando somente funções próprias do flask ou python para gerar as métricas:

```
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
```

Criamos uma variável global, e acessamos ela externamente para registrar o numero de requisições na pagina do Hello World e também criamos outra rota para exibir a métrica. Claro que isso é o exemplo mais simples possível. Mas serve somente para entendermos como podemos fazer para expor métricas.


#Fase 2: criando uma métrica através da lib do prometheus e excrevendo em um arquivo

Um meio mais completo é usar a própria lib do prometheus para armazenar e extrair esses dados, um modelo inicial seria:

```
from flask import Flask
from prometheus_client import Counter, Gauge, CollectorRegistry, write_to_textfile

app = Flask(__name__)

registry = CollectorRegistry()
c = Counter('requests_total', 'Description of counter', registry=registry)
app_version = Gauge('my_app_version', 'Description of gauge', registry=registry)
app_version.set(1.1)

@app.route('/metrics')
def prometheus_metrics():
    write_to_textfile('app.prom', registry)
    return 'metrics write'

@app.route('/')
def hello_world():
    c.inc()
    return 'Hello, World!'
```

Antes de executar temos que instalar a lib do prometheus_client:

```
pip install prometheus-client
flask run
```

Aqui criamos um CollectorRegistry, que é uma maneira de juntar todas as nossas métricas, e logo depois iniciamos duas métricas, um counter e um gauge. O que fazemos agora na rota de `metrics` é escrever em um arquivo .prom as métricas que coletamos naquele registry. Isso pode ser util quando vc ja tem o node_exporter instalado no servidor e quer que ele exporte para o prometheus essas métricas para vc.

## Fase 3: Exportando os dados através da lib do prometheus

Mas o meio mais comum é o prometheus buscar as requisições através de um http server, e é como vamos desenvolver agora.

```
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
```

Aqui ainda vamos precisar instalar mais o uwsgi:

```
pip install uwsgi
uwsgi --http 127.0.0.1:5000 --wsgi-file app.py --callable app
````

Acessando as paginas conseguimos ver as métricas e e gerar estatísticas acessando a pagina inicial. Ainda na biblioteca do python tem muitas outras métricas como Histogram e também outras formas de exportar as métricas como pushgateway.

A documentação é bastante completa e ajuda bastante na hora de fazer a aplicação.

https://github.com/prometheus/client_python
