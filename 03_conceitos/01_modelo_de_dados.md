# Modelo de Dados

Como ja comentamos o Prometheus armazena os dados como time series, em português algo como Série temporal, ou seja são uma coleção de observações ao longo do tempo. Se imaginarmos uma linha do tempo no eixo X, e irmos marcando os valores de uma determinada métrica no eixo Y, isso é um time series database.

Toda a métrica no Prometheus é composta de um timestamp, ou seja a data da coleta, e um metric name, ou nome da métrica. O métric name é a chave pela qual podemos acessar aquela métrica. Ele é composto por letras e números, pode conter underlines e dois pontos como separadores, apesar do dois pontos ser um caso especial geralmente usado em *recording rules* que veremos adiante.

Os metric names ficam algo como `http_requests_total`, que significa que é o numero total de requisições http recebidas por aquele serviço. É importante tentar usar metrics names que signifiquem o que aquela métrica representa.

Os metrics names podem conter labels, e esse é um recurso especialmente util, serve para categorizar as métricas que possam pertencer a serviços diferentes, as labels também podem conter letrar e números e underlines. Usamos as labels para diferenciar as métricas baseadas em suas características.

Por exemplo, usando a metric name acima, podemos criar as labels: http_requests_total{method="GET", handler="/messages"}, que significa que esse grupo de métricas é referente a requisições do tipo GET e que foram atendidas pelo /messages. Com isso conseguimos individualizar essa métricas para ter valores mais específicos, mas se quisermos em algum momento agrupar ou somar todas as http_requests_total também podemos fazer isso de forma fácil.

## Best practices

Uma boa pratica nos metrics names é usar prefixos que possam indentificar a quem a métrica pertence, como o nome da aplicação, ou métricas genéricas podem conter um nome mais amplo fazendo referencia ao que elas pertencem, exemplos:

- prometheus_notifications_total (especifica do Prometheus server)
- process_cpu_seconds_total (exportado por muitas client libraries)
- http_request_duration_seconds (para todas as requisições HTTP)

Métricas devem ter uma unidade somente, não misturar segundos com milesegundos, ou segundos com bites, usar sufixos para identificar a unidade pode ser uma boa ideia também. Quando for usar contagem acumulada podemos usar o sufixo total.

- http_request_duration_seconds
- node_memory_usage_bytes
- http_requests_total (para uma contagem acumulativa sem unidades)
- process_cpu_seconds_total (para uma contagem acumulativa com unidade)
- foobar_build_info (para uma métrica que prove uma metadata sobre uma aplicação)

Para uma melhor compatibilidade com as funções do Prometheus as métricas devem usar as unidades bases segundos, bytes e metros. Não usar millisegundos, megabytes, kilometros.
