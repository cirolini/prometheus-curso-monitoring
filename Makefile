# Curso de monitoracao com Prometheus - atalhos do lab.
#
#   make up     sobe o lab inteiro no Docker
#   make down   derruba e limpa
#   make k8s    cria um cluster kind com o kube-prometheus-stack
#
# Requisitos: docker + compose. Para o make k8s, tambem kind, kubectl e helm.

COMPOSE := docker compose -f labs/docker-compose.yml --env-file labs/.env
KIND_CLUSTER := curso-prometheus

.DEFAULT_GOAL := help
.PHONY: help up down logs ps reload validate k8s k8s-down k8s-forward

help:
	@echo "Lab do curso de monitoracao com Prometheus"
	@echo ""
	@echo "  make up        sobe Prometheus, Alertmanager, Grafana e os exporters"
	@echo "  make down      derruba tudo e apaga os volumes"
	@echo "  make ps        mostra o estado dos containers"
	@echo "  make logs      segue os logs"
	@echo "  make reload    recarrega a config do Prometheus sem reiniciar"
	@echo "  make validate  valida as configs com promtool/amtool"
	@echo ""
	@echo "  make k8s       cria o cluster kind e instala o kube-prometheus-stack"
	@echo "  make k8s-down  apaga o cluster kind"

up:
	$(COMPOSE) up -d --build
	@echo ""
	@echo "Lab no ar:"
	@echo "  Prometheus    http://localhost:9090"
	@echo "  Alertmanager  http://localhost:9093"
	@echo "  Grafana       http://localhost:3000   (admin / admin)"
	@echo "  App exemplo   http://localhost:5000   (/metrics, /erro)"
	@echo "  Pushgateway   http://localhost:9091"
	@echo "  cAdvisor      http://localhost:8080"
	@echo "  node_exporter http://localhost:9100/metrics"
	@echo "  blackbox      http://localhost:9115"

down:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f

reload:
	@curl -fsS -X POST http://localhost:9090/-/reload && echo "config recarregada"

validate:
	$(COMPOSE) run --rm --no-deps --entrypoint promtool prometheus \
		check config /etc/prometheus/prometheus.yml
	$(COMPOSE) run --rm --no-deps --entrypoint amtool alertmanager \
		check-config /etc/alertmanager/alertmanager.yml

k8s:
	kind create cluster --name $(KIND_CLUSTER) --config labs/k8s/kind-cluster.yaml
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install monitoring prometheus-community/kube-prometheus-stack \
		--namespace monitoring --create-namespace \
		--values labs/k8s/kube-prometheus-stack-values.yaml \
		--wait --timeout 15m
	@echo ""
	@echo "Cluster pronto. Para acessar:  make k8s-forward"

k8s-forward:
	@echo "Grafana em http://localhost:3000 (admin / prom-operator). Ctrl-C para sair."
	kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80

k8s-down:
	kind delete cluster --name $(KIND_CLUSTER)
