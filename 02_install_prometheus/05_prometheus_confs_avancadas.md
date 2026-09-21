# Configurações avançadas do Prometheus

A instalação que fizemos antes é simples e pode servir para os casos mais simples, mas devemos ter atenção em mais alguns parâmetros de configuração que podem ser necessários para executar o Prometheus em produção.

Algumas configurações importantes sobre como tratamos os dados e que devem ser colocadas como parâmetros de inicialização:

## Configurações de incialização

* --storage.tsdb.path: Onde o prometheus guarda os dados, o default é o `data/`. Ele é util caso você use uma partição ou disco separado para armazenar os dados. Pode ser uma boa ideia quando vc precisa guardar muitos dados, ou se vai usar um disco com mais performance como um ssd ou nvme.
* --web.enable-lifecycle: capacidade de fazer o reload do prometheus pela interface web, mandando um `POST` para `/-/reload`
* --config.auto-reload: faz o Prometheus ficar de olho no arquivo de configuração e recarregar sozinho quando ele mudar, sem precisar de reload manual. Combina muito bem com ambientes onde a configuração é gerada por alguma automação.
* --web.enable-otlp-receiver: habilita o endpoint que recebe métricas via OpenTelemetry (OTLP) direto no Prometheus, sem precisar de um collector no meio do caminho.
* --web.enable-admin-api: libera as APIs administrativas, como apagar séries. Cuidado ao habilitar em produção.

## Retenção de dados

A retenção costumava ser configurada por parâmetro de inicialização, com o `--storage.tsdb.retention.time` e o `--storage.tsdb.retention.size`. Eles ainda funcionam, mas estão marcados como *deprecated*, o lugar certo hoje é o próprio arquivo de configuração:

```
storage:
  tsdb:
    retention:
      time: 30d
      size: 10GB
```

* time: o tempo que o Prometheus vai guardar os dados, o default é 15 dias, então se você pretende que os dados tenham mais tempo precisamos alterar esse valor.
* size: valor máximo para utilizar de espaço em disco, é util para não ocupar todo o espaço em disco disponivel.

A vantagem de estar no arquivo de configuração é que agora você consegue mudar a retenção com um reload, sem precisar reiniciar o serviço.

# Arquivo de configuração

Agora um passo importante é entender o arquivo de configuração do Prometheus:

* global.scrape_interval: default 1 minuto. Intervalo de tempo que o Prometheus vai usar para coletar as informações dos targets. Ou seja, ele vai coletar metricas uma vez a cada minuto no valor default.
* global.evaluation_interval: default 1 minuto. Tempo que o Prometheus usa para avaliar as regras e gerar alertas. Repare que o arquivo de exemplo que vem com o pacote coloca 15s, mas o default de verdade é 1 minuto.
* rule_files: Aqui vamos colocar as regras de alertas e também de recording rules.
* scrape_configs: onde vamos colocar os jobs que o Prometheus vai usar para coletar metricas. Os jobs podem ter diversas configurações que vamos ver mais adiante.
* storage: as configurações de armazenamento que vimos acima, como a retenção.
* otlp: as configurações de como tratar as métricas que chegam via OpenTelemetry, quando você habilita o receiver.

Uma dica que vale para o arquivo inteiro: sempre valide antes de aplicar, com `promtool check config /etc/prometheus/prometheus.yml`. É muito mais barato descobrir um erro de indentação ali do que depois de um reload que não subiu.

No decorrer do curso vamos ver como acrescentar novas configurações e novos jobs.
