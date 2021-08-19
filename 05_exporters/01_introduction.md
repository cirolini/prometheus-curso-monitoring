# Os Exporters

Como ja vimos antes, o Prometheus faz o scrap das métricas em outras aplicações para coletar os dados dos servidores ou de aplicações. Essas aplicações que coletam as métricas são os exporters, elas de alguma forma pegam os dados convertem em métricas e geralmente exportam isso via uma porta http para que o Prometheus possa coletar essas informações de tempos em tempos.

Existem uma infinidade de exporters não oficiais, pessoas que passaram por determinado problema com uma aplicação/hardware e fizeram um exporter e divulgam isso em algum github opensource. Mas também existem exporter oficiais, ou seja, aqueles que são mantidos pela equipe do Prometheus, ou pela comunidade de algum software, e que em geral são bem confiáveis.

Para ter acesso a uma lista bem completa dos exporters podemos ver eles diretamente no site oficial: https://prometheus.io/docs/instrumenting/exporters/

Obviamente você também pode criar o seu exporter, é um dos assuntos que vamos cobrir em um capitulo especifica. Existe uma série de bibliotecas prontas para diversas linguagens de programação que fazem isso.

Não vamos falar sobre todos os exporters, mas vamos tentar cobrir alguns dos principais.

- node_exporter, exporter para métricas de hardware e sistema opercional unix (linux).
- mtail_exporter, ferramenta desenvolvida pelo Google para exportar métricas baseado em logs de aplicação usando expressão regulares.
- pushgateway, quando vc tem alguma ferramenta do tipo cronjobs, ou funções serverless, pode ser interessante enviar os dados para o Prometheus, nesse caso você pode usar o pushgateway para a sua aplicação enviar os dados ao invez do Prometheus ir buscar os mesmos.
- blackbox_exporter, usado para fazer testes HTTP, HTTPS, DNS, TCP and ICMP em um endpoint ou aplicação.
- cadvisor, analisa o uso de recursos e performance de containers.
- snmp_exporter, exporter de dados via SNMP, ideal para compatibilidade de aplicações mais antigas, switchs e afins,
- aws cloud watch exporter, server para coletar dados do cloud watch da AWS e inserir no Prometheus.
