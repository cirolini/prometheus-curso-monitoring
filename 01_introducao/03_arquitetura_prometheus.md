# Arquitetura do Prometheus

Como vimos antes o Prometheus é composto de uma série de ferramentas que se comunicam para gerar estatísticas e métricas para os mais diversos tipos de serviços e aplicações.

## Caracteristicas

- Prometheus é um banco de dados do tipo **time series**, com dados identificados por um nome da métrica e pares de chave e valores.
- Tem uma linguagem de consulta flexível, a **PromQL**, onde pode extrair e modelar os dados para revelar informações relevante
- Nodos são **autônomos**, ou seja, não trabalham em cluster
- A coleta de dados é feita por HTTP, ou seja, é o Prometheus server que vai até os servidores e aplicações coletar os dados via o protocolo http
- O envio de dados para o Prometheus é feito através do **pushgateway**, ou seja quando a tua aplicação necessita enviar dados para o Prometheus, como por exemplo uma função serverless que execute em um determinado horario pode querer enviar os dados ao contraria de esperar o Prometheus coletar os dados
- Novas aplicações e serviços podem ser monitoradas através de **service discovery** ou arquivos de configuração

## Componentes

![prom_architecture](images/prom_architecture.png "Prometheus Architecture")

- O **Prometheus server** é quem coleta e armazena a informação. É o core, ou o centro de todas as ferramentas.
- **bibliotecas para clientes**, ou seja, bibliotecas em varias linguagem de programação como Python ou Go que vamos falar mais para frente para incorporar métricas na sua aplicação
- o **push gateway** é uma forma de enviar dados para o Prometheus para aplicações de curta duração
- **exporters**, são aplicações que servem para extrair dados de determinado sistema ou aplicação, como por exemplo o node_exporter que coleta dados de sistemas linux, como uso de CPU, disco, memória etc, mysql_exporter que pega estatísticas do mysql, o snmp_exporter que pode ser utilizado para integrar com monitorações SNMP, ou o cadvisor que coleta estatísticas sobre containers.
- o **Alertmanager** que serve para lidar com alertas, integrar com ferramentas externas, como email, slack, Pagerduty ou Opsgenie.
- e ainda varias outras ferramentas, por exemplo como o promctl, que é uma ferramenta linha de comando que facilita a interação com o Prometheus.
- **Grafana**, é uma ferramenta a parte mas em geral são usados em conjunto, é usado para a visualização das metricas e criação de dashboards.

### Para que ele serve

Geralmente o Prometheus é utilizado para monitoração de sistemas e aplicações, a arquitetura de standalone node da uma segurança que você vai conseguir ver os dados mesmo em um momento de problema de redes, ou em outros tipos de problemas que cluster podem trazer.

### Para o que ele não serve

O Prometheus não deve ser utilizado para a bilhetagem de sistemas, ou para sistemas onde precisam de 100% de precisão. Obviamente os sistemas do Prometheus são precisos, mas trabalham com estatística e amostragem para tornar a visualização de dados mais rápida.

## Conclusão

Agora que entendemos como o Prometheus funciona vamos falar um pouco sobre modelos de monitoração e o que devemos monitorar em cada sistema.
