# Node Exporter

O Node exporter provavelmente seja um dos exporter mais utilizados. Ele server para coletar métricas de hardware e Sistema Operacional Unix, coisas como uso de processador, disco, memória. Mas ele não tem informações somente informações simples, tem detalhes bem profundos do sistema operacional que ajudam a debugar problemas bem complexos.

## Instalando o node exporter

Para instalar o node_exporter vamos continuar na nossa VM e vamos usar um procedimento muito parecido com o que ja fizemos antes:

```
wget https://github.com/prometheus/node_exporter/releases/download/v*/node_exporter-*.*-amd64.tar.gz
tar xvfz node_exporter-*.*-amd64.tar.gz
cd node_exporter-*.*-amd64
./node_exporter
```

Para poder ver as métricas que ele ja esta coletando:

```
curl http://localhost:9100/metrics
```

Vamos aproveitar e configurar para o node_exporter rodar como serviço:

```
sudo useradd --no-create-home --shell /bin/false node_exporter
sudo mv node_exporter /usr/local/bin

sudo chown node_exporter:node_exporter /usr/local/node_exporter
```

Criando o arquivo do systemd.

```
sudo vim /etc/systemd/system/node_exporter.service

[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Agora iniciamos o node_exporter e colocamos ele para iniciar junto com o Sistema Operacional.

```
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl status node_exporter
sudo systemctl enable node_exporter
```

## Configurando o Prometheus para buscar as métricas

Precisamos configurar o prometheus para começar a coletar as estatiscas:

```
scrape_configs:
- job_name: node_exporter
  static_configs:
  - targets: ['localhost:9100']
```

Para começarmos a analisar os dados do node_exporter ja podemos usar a query language para ver alguns dados:

- `rate(node_cpu_seconds_total{mode="system"}[1m])`:	A quantidade média de tempo de CPU gasto no modo de sistema, por segundo, durante o último minuto (em segundos)
- `node_filesystem_avail_bytes`:	O espaço do sistema de arquivos disponível para usuários não root (em bytes)
- `rate(node_network_receive_bytes_total[1m])`:	O tráfego médio de rede recebido, por segundo, no último minuto (em bytes)

Uma dica muito boa é que vcs instalem no Grafana o dashboard Node Exporter Full, onde ele ja vem com as mais diversas métricas em tráficos separados por contexto, que é extremamente util para visualizar e explorar essas métricas: https://grafana.com/grafana/dashboards/1860

![grafana_node_exporter_full](https://grafana.com/api/dashboards/1860/images/7994/image "Grafana Node Exporter Full")
