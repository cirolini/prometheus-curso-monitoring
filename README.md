# Curso de monitoração com o Prometheus

> **In English:** a free, hands-on Prometheus + Grafana course written in Brazilian Portuguese. Ten modules covering architecture, installation, PromQL, exporters, alerting, Kubernetes, advanced topics, monitoring philosophy, and — new in the 2026 edition — observing LLM and agent-based applications. Every lab runs on a laptop with a single `make up`. Updated for Prometheus 3.x, Alertmanager 0.34, Grafana 13 and kube-prometheus-stack.

Esse curso ensina como usar o Prometheus como uma ferramenta integrada de monitoração, entender seus conceitos, usar grande parte de seu ecossistema, e ainda usar o Grafana para gerar dashboards.

Vamos cobrir um grande número de tópicos, todos eles com exemplos práticos. Vamos falar sobre a instalação tanto em servidores físicos quanto em Kubernetes. Falar sobre como fazer consultas que tragam informações relevantes, como gerenciar alertas, até mesmo como prever o futuro.

Quero mostrar como usar os exporters e também gerar os seus próprios. Por fim vamos ver alguns aspectos avançados, entender alguns conceitos sobre monitoração e alertas, e — na edição 2026 — como observar aplicações que chamam modelos de linguagem.

## Para quem é

Para quem cuida de sistema em produção e quer parar de descobrir problema pelo cliente. Não precisa saber Prometheus; precisa estar confortável com linha de comando Linux e ter uma noção de Docker.

Se você é desenvolvedor e nunca instrumentou uma aplicação, o módulo 05 é para você. Se você é SRE e já usa Prometheus, provavelmente vai querer pular direto para os módulos 06 em diante.

## O que você vai saber fazer no fim

- instalar e operar Prometheus, Alertmanager e Grafana, em Linux e em Kubernetes
- escrever PromQL que responde perguntas de verdade, não só `up == 0`
- escolher o tipo certo de métrica e instrumentar a sua própria aplicação
- criar alertas que representam problemas, e não barulho
- prever um problema antes de ele acontecer, com `predict_linear` e baselines
- detectar anomalia com z-score
- observar uma aplicação que chama LLM: latência de cauda longa, custo, tokens e agentes

## Subindo o ambiente

Não precisa instalar nada à mão para começar. Na raiz do repositório:

```
make up
```

Isso levanta Prometheus, Alertmanager, Grafana (com datasource e dashboards já provisionados), node_exporter, blackbox_exporter, pushgateway, cAdvisor, uma aplicação de exemplo e a aplicação de IA do módulo 10 — essa em modo simulado, sem precisar de chave de API nenhuma.

| | |
|---|---|
| Prometheus | http://localhost:9090 |
| Alertmanager | http://localhost:9093 |
| Grafana | http://localhost:3000 (`admin` / `admin`) |
| App de IA | http://localhost:8000 |

Para derrubar: `make down`. Para a parte de Kubernetes, `make k8s` cria um cluster [kind](https://kind.sigs.k8s.io/) com o kube-prometheus-stack instalado.

Detalhes, portas e as versões de tudo estão em [`labs/`](labs/). As lições de instalação manual continuam no curso e valem a pena — é nelas que você entende o que acontece por baixo. O lab é o caminho rápido para quando você quer praticar a consulta e não montar o ambiente de novo.

**Requisitos:** Docker (ou [colima](https://github.com/abiosoft/colima)) e `make`. Para `make k8s`, também `kind`, `kubectl` e `helm`.

## Sumário

### Introdução
1. [Introdução](01_introducao/01_introducao.md)
1. [Apresentação do Instrutor](01_introducao/02_apresentacao_instrutor.md)
1. [Arquitetura do Prometheus](01_introducao/03_arquitetura_prometheus.md)
1. [Conceitos do Alertmanager](01_introducao/04_alertmanager.md)

### Instalando o ambiente
1. [Instalando o Prometheus no Linux](02_install_prometheus/01_install_prometheus_linux.md)
1. [Instalando o Alertmanager no Linux](02_install_prometheus/02_install_alertmanager_linux.md)
1. [Instalando o Grafana no Linux](02_install_prometheus/03_install_grafana.md)
1. [Criando os primeiros alertas](02_install_prometheus/04_criando_alertas.md)
1. [Configurações avançadas do Prometheus](02_install_prometheus/05_prometheus_confs_avancadas.md)
1. [Criando todo ambiente no Docker](02_install_prometheus/06_docker.md)

### Prometheus Conceitos
1. [Modelo de dados](03_conceitos/01_modelo_de_dados.md)
1. [Tipos de Métricas](03_conceitos/02_tipos_de_metricas.md)
1. [Jobs e Instances](03_conceitos/03_jobs_instances.md)

### Querying Prometheus
1. [Básico](04_querying/01_basico.md)
1. [Operators](04_querying/02_operator.md)
1. [Funções](04_querying/03_functions.md)
1. [Recording Rules](04_querying/04_recording_rules.md)
1. [API HTTP](04_querying/05_api_http.md)

### Exporters
1. [Introdução aos Exporters](05_exporters/01_introduction.md)
1. [node_exporter](05_exporters/02_node_exporter.md)
1. [mtail_exporter](05_exporters/03_mtail_exporter.md)
1. [pushgateway](05_exporters/04_pushgateway.md)
1. [blackbox_exporter](05_exporters/05_blackbox_exporter.md)
1. [cadvisor](05_exporters/06_cadvisor.md)
1. [Criando o seu Exporter](05_exporters/07_escrevendo_exporters.md)

### Alerting
1. [Criando seu primeiro alerta](06_alerting/01_criando_alertas.md)
1. [Alertas prevendo o futuro usando predict_linear](06_alerting/02_predict_linear.md)
1. [Integrando com Email](06_alerting/03_notificando_email.md)
1. [Integrando com o Slack](06_alerting/04_integrando_slack.md)
1. [Silenciando alertas](06_alerting/05_silence.md)

### Integrando com o Kubernetes
1. [Instalando o Prometheus no Kubernetes](07_kubernetes/01_install_prometheus_on_k8s.md)
1. [Grafana no Kubernetes](07_kubernetes/02_install_grafana_on_k8s.md)
1. [Alertando no Kubernetes](07_kubernetes/03_alerting_k8s.md)
1. [Service Discovery](07_kubernetes/04_service_discovery.md)

### Aspectos Avançados
1. [Federation](08_advanced_topics/01_federation.md)
1. [Management API](08_advanced_topics/02_management_api.md)
1. [Baselines](08_advanced_topics/03_baselines.md)
1. [Z-Score](08_advanced_topics/04_anomaly_detection.md)

### Conclusão
1. [Modelos de monitoração](09_conclusion/01_modelos_de_monitoracao.md)
1. [Alertando sobre os sintomas (Alert on the user experience)](09_conclusion/02_alerting_on_symptoms.md)
1. [Conclusão](09_conclusion/03_conclusion.md)

### Observando aplicações com IA
1. [O que muda quando a aplicação chama um LLM](10_observando_ia/01_o_que_muda.md)
1. [Instrumentando uma chamada de LLM](10_observando_ia/02_instrumentando.md)
1. [Convenções do OpenTelemetry para GenAI](10_observando_ia/03_opentelemetry_genai.md)
1. [Dashboards e alertas para IA](10_observando_ia/04_dashboards_e_alertas.md)
1. [Observando um agente](10_observando_ia/05_observando_agente.md)

## Edição 2026

O curso foi escrito em 2020 e 2021, quando o Prometheus estava na série 2.x. Esta edição atualizou tudo que envelheceu e acrescentou o módulo 10. As mudanças estão no [CHANGELOG](CHANGELOG.md), e o levantamento que motivou cada uma está em [`docs/audit-2026.md`](docs/audit-2026.md).

Em resumo: Prometheus 3.14, Alertmanager 0.34, Grafana 13, kube-prometheus-stack no lugar do chart antigo, labs que sobem com um comando, e um módulo novo sobre observar aplicações com IA.

## Contribuindo

Achou erro, link quebrado ou coisa que envelheceu? Abra uma issue ou um PR. O curso é mantido em aberto justamente por isso.

Rafael Cirolini — rafael@cirolini.com.br
