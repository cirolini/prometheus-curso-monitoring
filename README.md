# Curso de monitoração com o Prometheus

Esse curso ensina como usar o Prometheus como uma ferramenta integrada de monitoração, entender seus conceitos, usar grande parte de seu ecossistema, e ainda usar o Grafana para gerar dashboards.

Vamos cobrir um grande número de tópicos, todos eles com exemplos práticos. Vamos falar sobre a instalação tanto em servidores físicos quando em Kubernetes. Falar sobre como fazer consultas que tragam informações relevantes, como gerenciar alertas, até mesmo como prever o futuro.

Quero mostrar como usar os exporters e também gerar os seus próprios. Por fim vamos ver alguns aspectos avançados e ainda entender alguns conceitos sobre a monitoração e alertas.

## Sumário

### Introdução
1. [Introdução](01_introducao/01_introducao.md)
1. [Apresentação do Instrutor](01_introducao/02_apresentacao_intrutor.md)
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
1. [Básico](04_quering/01_basico.md)
1. [Operators](04_quering/02_operator.md)
1. [Funções](04_quering/03_functions.md)
1. [Recording Rules](04_quering/04_recording_rules.md)
1. [API HTTP](04_quering/05_api_http.md)

### Exporters
1. [Introdução aos Exporters](05_exporters/01_introduction.md)
1. [node_exporter](05_exporters/02_node_exporter.md)
1. [mtail_exporter](05_exporters/03_mtail_exporter.md)
1. [pushgateway](05_exporters/04_pushgateway.md)
1. [blackbox_exporter](05_exporters/05_blackbox_exporter.md)
1. [cadvisor](05_exporters/06_cadivisor.md)
1. [Criando o seu Exporter](05_exporters/07_escrevendo_exporters.md)

### Alerting
1. [Criando seu primeiro alerta](06_alerting/01_criando_alertas.md)
1. [Alertas prevendo o futuro usando predict_linear](06_alerting/02_predict_linear.md)
1. [Integrando com Email](06_alerting/03_notificando_email.md)
1. [Integrando com o Slack](06_alerting/04_integrando_slack.md)
1. [Silenciando alertas](06_alerting/05_silence.md)

### Integrando com o Kubernetes
1. [Instalando o Prometheus no Kubernetes](/07_kubernetes/01_install_prometheus_on_k8s.md)
1. [Instalando o Grafana no Kubernetes](/07_kubernetes/02_install_grafana_on_k8s.md)
1. [Alertas no Kubernetes](/07_kubernetes/03_alerting_k8s.md)
1. [Service Discovery](/07_kubernetes/04_service_discovery.md)

### Aspectos Avançados
1. [Federation](/08_advanced_topics/01_federation.md)
1. [Management API](/08_advanced_topics/02_management_api.md)

### Conclusão
1. [Modelos de monitoração](/09_conclusion/01_modelos_de_monitoracao.md)
1. [Alertando sobre os sintomas (Alert on the user experience)](/09_conclusion/02_alerting_on_sitoms.md)
1. [Conclusão](/09_conclusion/03_conclusion.md)
