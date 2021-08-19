# Os 4 sinais de ouro do Observability

Referenica no livro do Google sobre SRE: https://landing.google.com/sre/sre-book/chapters/monitoring-distributed-systems/#xref_monitoring_golden-signals

Uma das grandes mudanças de um time de SRE é a forma de pensar a monitoração dos seus sistemas. Em tempos muito antigos, onde as aplicações "eram mato", nossas monitorações eram baseadas somente em alguns status de hardware, rede e se determinado serviço estava up ou down.

A mudança de foco agora é mudar os indicadores para aquilo que importa para o usuário, como saber se um serviço esta lento, entregando erros, impreciso, ou fazendo algo diferente do que deveria.

Todos os exemplos aqui são feitos usando a query language do Prometheus e os gráficos são visualizados no Grafana.

# The Four Golden Signals
No livro do Google sobre SRE, um dos capítulos trata sobre 4 principais sinais que deveríamos monitorar em qualquer aplicação.

##Latência

Uma métrica impacta diretamente os nossos usuários, um sistema lento pode ser pior que um sistema não funcionando em alguns casos.
As formas mais comuns de visualizar isso no Prometheus é usar a query function histogram_quantile(), que vai nos dar uma média de tempo das requisições de uma aplicação sob um determinado percentil.

O gráfico acima mostra a média de tempo de resposta de uma aplicação, olhando o 95, 90, 75 e 50 percentil das mesmas. A expressão usada para gerar o gráfico esta abaixo, mudando somente o primeiro campo do percentil.
`histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[10m]))``

O histogram quantile podem ser um pouco complexo a primeira vista, mas é uma maneira muito inteligente de calcular tempos de resposta sem ter que calcular cada requisição individualmente, não pretendo explicar como eles funcionam aqui, no blog Robust Perception tem um post muito bom explicando como funcionam.

Um alerta para esse tipo de monitoração poderia ser algo como:
```
- alert: "Webserver 95th Percentile Latency is bigger than 400ms"
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[10m])) by (le)) > 0.4
    for: 15m
    labels:
      severity: moderate
```

Essa monitoração gera um alerta caso a média do tempo de respostas de 95 percentil das requisições forem maior de 400 milissegundos por 15 minutos com uma criticidade moderada.

##Tráfego

A quantidade de trabalho que esta sendo feito, no caso de aplicações web, uma das métricas pode ser por exemplo o número de requisições que o webserver esta atendendo, ou para algum serviço de streaming os usuários simultâneos, ou ainda a quantidade de bytes enviados.

Esse gráfico por exemplo é o numero de requisições por segundo de um servidor rodando nginx, dividido em total de requests e número de requests no status writing.
`rate(nginx_connections_processed_total{stage="any"}[1m])`

A função rate calcula a média de requisições por segundo de um período de tempo, no caso do exemplo 1 minuto.
Esses casos em geral não possuem alertas atrelados, são somente gráficos para que possamos correlacionar com outros problemas. Um tipo de alerta poderia ser um tráfico baixo além do esperado, poderia indicar algum problema em alguma plataforma causando falhas de entrega ou algo assim, de qualquer forma seria um evento correlacionado e alertas tem que gerar ações, nesse caso pode ser difícil correlacionar.

## Erros

Esse é simples, é a quantidade de erros que a tua aplicação esta retornando para os seus usuários. Um servidor web poderia estar entregando erros 5XX, ou uma aplicação de outro gênero poderia estar negando requisições.

Esse gráfico mostra o somatório de todas as requisições com status 5XX de uma aplicação web.
`sum(rate(webserver_requests{status=~"5[0-9][0-9]"}[1m]))``

A expressão acima é a soma de todos os servidores da média das requisições por segundo com status 5XX.
Aqui os alertas podem ser de diversos tipos, um modelo que eu gosto é o percentual de erros/sucessos de uma aplicação, por exemplo:
```
- alert: "Webserver errors rate is above 1%"
    expr: sum(rate(webserver_requests{status!~"5.."}[1m]) * 100) / sum(rate(webserver_requests[1m])) < 99
    for: 15m
    labels:
      severity: high
```

Esse alerta acima pega a soma de todos os servidores da média de requisições que não foram um erro (diferentes de 5xx) e divide pelo total de requisições, com isso temos o nosso percentual de sucesso em alguns casos conhecido com SLO de Availability (disponibilidade) caso ele caia abaixo de 99% por 15 minutos gera um alerta para verificação.

## Saturação

Precisamos saber o quanto dos recursos que disponibilizaram estão ocupados, os recursos aqui podem ser de todos os tipos, usos de hardware como CPU, Memória ou disco. Existem outros recursos, como indicadores de sistema operacional como context switching, load e contrack. Ou também sistemas de filas, storage entre muitos outros.

Nesse gráfico acima temos uma série de indicadores de saturação, como CPU, memória entre outros. Esses dados foram exportados usando o Node Exporter, e visualizados usando o dashboard Node Exporter Full.
`100 - ((node_memory_MemAvailable_bytes{instance="$node"} * 100) / node_memory_MemTotal_bytes{instance="$node"})``

O exemplo da query acima mostra o uso de memória RAM, é o calculo da divisão entre a memória disponível e a memória total, para saber percentualmente a saturação.

Os alertas de saturação podem cobrir os mais diversos tipos de problemas, o exemplo acima poderia gerar um alerta sobre o uso de memória por exemplo:
```
- alert: "Webserver Memory High"
    expr: 100 - ((node_memory_MemAvailable_bytes{instance="$node"} * 100) / node_memory_MemTotal_bytes{instance="$node"}) > 90
    for: 15m
    labels:
      severity: low
```

Esse alerta verifica se um servidor esta com 90% da memória total utilizada pelos últimos 15 minutos.

## Conclusão
Essas são as principais métricas ou indicadores que qualquer sistema deveria ter de indicadores e alertas. São feitas de forma genérica, onde devem se enquadrar na maioria dos sistemas.

Quanto mais indicadores e informações você tiver sobre o seu sistema mais fácil vai ser entender os comportamentos do mesmo e saber como atuar de forma mais rápida e efetiva.
