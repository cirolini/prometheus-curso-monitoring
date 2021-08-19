# Usando o Prometheus com o Docker

Uma das maneiras mais fáceis de testar o Prometheus é executando ele diretamente como um container no Docker. Primeiro você precisa ter o docker instalado no seu computador, basta ir na pagina https://www.docker.com/get-started e baixar o Docker para desktop e depois instalar.

Na pagina oficial do docker hub, tem a imagem do container e alguma informação relevante: https://hub.docker.com/r/prom/prometheus/

Depois do Docker instalado e inicializado no seu computador basta rodar:

```
docker run -p 9090:9090 prom/prometheus
```

Com isso você ja vai conseguir acessar o seu navegador na pagina http://localhost:9090/ para acessar o painel do Prometheus, e com a configuração default ele ja esta se auto monitorando.

Para customizar o arquivo de configuração do prometheus basta:

```
docker run -p 9090:9090  -v ${PWD}/docker/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

## Customizando o Dockerfile

Ou até mesmo se você quiser fazer uma imagem personalizada do Docker com mais algumas opções ou instalando algum tipo de pacote adicional você pode fazer assim, basta criar um arquivo com o nome Dockerfile com o seguinte conteúdo:

```
FROM prom/prometheus
ADD docker/prometheus.yml /etc/prometheus/
```

Depois fazer o build da imagem e executar o container:

```
docker build -t my-prometheus .
docker run -p 9090:9090 my-prometheus
```

# Prometheus Docker lab

Agora ja aprendemos a executar o Prometheus como um container e outras maneiras de fazer isso, vamos usar o docker compose para integrar um ambiente com o Prometheus e outros componentes ja configurados.

```
git clone https://github.com/cirolini/prometheus-lab
cd prometheus-lab/
docker-compose up
```

Com isso ja temos uma infra estrutura completa com o Prometheus, Alertmanager, Grafana, node_exporter, mtail_exporter, cadvisor e blackbox, vamos falar mais sobre todos esses componentes depois mas agora podemos olhar um pouco o arquivo de configuração do docker compose, e depois acessar alguns links interessantes para entender como funciona a integração entre os compontes.

* Prometheus: http://127.0.0.1:9090/
* Alerting Manager: http://127.0.0.1:9093/
* Grafana: http://127.0.0.1:3000/
* Node Exporter: http://127.0.0.1:9100/
* Mtail Exporter: http://127.0.0.1:3903/

Se olharmos o arquivo do docker-compose (docker-compose.yml), vamos ver que levantamos vários container com cada aplicação ja montando os volumes corretos e também com seus arquivos de configuração.

Além disso ja vem com alertas configurados, graficos e o how-to de uso do lab ja explica como simular alertas e verificar dados em graficos.

Mais para a frente vamos aprender como usar tudo no Kubernetes, mas para isso vamos ter um módulo inteiro.
