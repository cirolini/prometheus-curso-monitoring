# Blackbox Exporter

Quando falamos em modelos de monitoração existem os tipos de whitebox, que é quando coletamos informações diretamente da aplicação ou dos logs, ou termos um agente diretamente instalado no servidor para coleta, e blackbox que é quando queremos simular um comportamento de usuário com a aplicação para testar o funcionando "olhando de fora".

Esse é o papel do blackbox_exporter. Ele server para fazer requisições HTTP, TCP, DNS entre outros para testar as nossas aplicações com uma visão do usuário.

Vamos usar o mesmo método para executar o blackbox exporter através de um container:

```
docker run -p 9115:9115 -d prom/blackbox-exporter
```

Agora ja temos um blackbox rodando em um container e escutando na porta 9115. Basta executarmos no browser uma requisição do tipo:

```
http://localhost:9115/probe?target=prometheus.io&module=http_2xx
```

![blackbox](/05_exporters/images/blackbox.png "Blackbox Exporter")

Isso vai fazer com que o blackbox faça uma requisição do tipo http para o site do prometheus.io e esperando que ele receba um 200 OK, ou seja, que a requisição foi um sucesso. O blackbox tbm vai trazer diversas informações uteis sobre o tempo da requisição, as fases, tipo do protocolo e versão do TLS.

A configuração do prometheus é bastante simples e similar as outras configurações:

```
scrape_configs:
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]  # Look for a HTTP 200 response.
    static_configs:
      - targets:
        - http://prometheus.io    # Target to probe with http.
        - https://prometheus.io   # Target to probe with https.
        - http://example.com:8080 # Target to probe with http on port 8080.
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115  # The blackbox exporter's real hostname:port.
```
