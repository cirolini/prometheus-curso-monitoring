# Configurações avançadas do Prometheus

A instalação que fizemos antes é simples e pode servir para os casos mais simples, mas devemos ter atenção em mais alguns parâmetros de configuração que podem ser necessários para executar o Prometheus em produção.

Algumas configurações importantes sobre como tratamos os dados e que devem ser colocadas como parâmetros de inicialização:

## Configurações de incialização

* --storage.tsdb.path: Onde o prometheus guarda os dados, o default é o `data/`. Ele é util caso você use uma partição ou disco separado para armazenar os dados. Pode ser uma boa ideia quando vc precisa guardar muitos dados, ou se vai usar um disco com mais performance como um ssd ou nvme.
* --storage.tsdb.retention.time: o tempo que o Prometheus vai guardar os dados, o default é 15 dias, então se você pretende que os dados tenham mais tempos precisamos alterar esse valor.
* --storage.tsdb.retention.size: Valor máximo para utilizar de espaço em disco, é util para não ocupar todo o espaço em disco disponivel.
* --web.enable-lifecycle: capacidade de fazer o reload do prometheus pela interface web

# Arquivo de configuração

Agora um passo importante é entender o arquivo de configuração do Prometheus:

* global.scrape_interval: default 1 minuto. Intervalo de tempo que o Prometheus vai usar para coletar as informações dos targets. Ou seja, ele vai coletar metricas uma vez a cada minuto no valor default.
* evaluation_interval: default é 15s. Tempo para o prometheus gerar alertas.
* rule_files: Aqui vamos colocar as regras de alertas e também de recording rules.
* scrape_configs: onde vamos colocar os jobs que o Prometheus vai usar para coletar metricas. Os jobs podem ter diversas configurações que vamos ver mais adiante.

No decorrer do curso vamos ver como acrescentar novas configurações e novos jobs.
