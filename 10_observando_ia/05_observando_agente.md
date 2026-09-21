# Observando um agente

Até aqui a aplicação fazia uma chamada ao modelo e devolvia a resposta. Um agente faz outra coisa: chama o modelo, olha o que veio, decide executar uma ferramenta, manda o resultado de volta, chama o modelo de novo, e repete até achar que terminou.

Isso muda a unidade de medida. A pergunta deixa de ser "quanto demorou a chamada?" e passa a ser **"quanto custou resolver a tarefa?"** — e a resposta agora envolve um número que você não controla: quantas voltas o agente deu.

O lab tem um agente de brinquedo em [`labs/llm-app/agent.py`](../labs/llm-app/agent.py). Ele não é inteligente — escolhe ferramenta por sorteio, de propósito. O que interessa é a forma do laço, não a qualidade da decisão.

```
curl -s -X POST localhost:8000/agent \
  -H 'content-type: application/json' \
  -d '{"prompt":"pesquise e resuma"}' | jq
```

```json
{ "outcome": "ok", "inference_calls": 3, "tool_calls": 2 }
```

## As três métricas que importam

### Passos por tarefa

```python
agent_inference_calls = Histogram(
    "gen_ai_invoke_agent_inference_calls",
    "Quantas chamadas ao modelo o agente fez numa execucao",
    ["gen_ai_agent_name"],
    buckets=(1, 2, 3, 5, 8, 12, 20, 30),
)
```

Esta é **a** métrica de agente. Se ela sobe sem a qualidade melhorar, o seu agente está rodando em círculo: chamando o modelo, recebendo algo que não resolve, tentando de novo. Cada volta é dinheiro e é latência.

O que torna isso perigoso é que **nenhuma métrica de chamada individual denuncia o problema**. A latência por chamada continua ótima, a taxa de erro continua zero, o custo por chamada continua o mesmo. Só o número de voltas cresce. Quem só instrumentou a chamada do modelo não vê nada.

### Execuções que esgotaram os passos

```python
agent_steps_exhausted = Counter(
    "gen_ai_invoke_agent_steps_exhausted_total", ..., ["gen_ai_agent_name"]
)
```

Todo agente precisa de um teto de passos — o do lab é 8. Bater nesse teto significa que o agente **desistiu sem resolver**, depois de gastar o orçamento inteiro da tarefa. É o pior resultado possível: custo máximo, entrega zero.

Esse contador merece alerta:

```yaml
- alert: AgenteRodandoEmCirculo
  expr: |
    sum(rate(gen_ai_invoke_agent_steps_exhausted_total[15m]))
      /
    sum(rate(gen_ai_invoke_agent_duration_seconds_count[15m]))
    > 0.15
  for: 15m
```

Mais de 15% das execuções esgotando os passos é sintoma de prompt ruim, ferramenta quebrada ou tarefa fora do alcance do agente.

### Duração por ferramenta

```python
tool_duration = Histogram(
    "gen_ai_execute_tool_duration_seconds",
    "Duracao da execucao de uma ferramenta",
    ["gen_ai_tool_name", "outcome"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
```

Aqui vem a descoberta que mais surpreende quem instrumenta agente pela primeira vez: **muitas vezes o gargalo não é o modelo, é uma ferramenta.**

Uma consulta a banco que demora 1,5s, chamada três vezes por tarefa, são 4,5 segundos que o usuário espera e que ninguém atribui ao lugar certo — todo mundo culpa "a IA". Separar a duração por ferramenta acaba com essa discussão em um gráfico.

A label `outcome` também importa: ferramenta que falha silenciosamente faz o agente dar mais voltas, e aí o sintoma aparece na métrica de passos sem que ninguém entenda por quê.

## O laço, instrumentado

```python
def run_agent(provider, task, agent_name="agente-demo"):
    started = time.perf_counter()
    inference_calls = 0
    tool_calls = 0
    outcome = "ok"

    try:
        for step in range(MAX_STEPS):
            inference_calls += 1
            try:
                provider.complete(f"[passo {step}] {task}")
            except ProviderError as e:
                m.errors_total.labels(provider.name, provider.model, e.error_type).inc()
                outcome = "error"
                break

            if random.random() < 0.45:      # o modelo "decide" que terminou
                break

            tool_name = random.choice(list(TOOLS))
            tool_calls += 1
            t0 = time.perf_counter()
            try:
                TOOLS[tool_name](task)
                tool_outcome = "ok"
            except Exception:
                tool_outcome = "error"
            finally:
                m.tool_duration.labels(tool_name, tool_outcome).observe(
                    time.perf_counter() - t0
                )
        else:
            outcome = "steps_exhausted"
            m.agent_steps_exhausted.labels(agent_name).inc()
    finally:
        m.agent_duration.labels(agent_name, outcome).observe(time.perf_counter() - started)
        m.agent_inference_calls.labels(agent_name).observe(inference_calls)
        m.agent_tool_calls.labels(agent_name).observe(tool_calls)
```

Duas construções de Python que fazem o trabalho pesado aqui.

O **`for/else`**: o bloco `else` de um `for` só roda se o laço terminou sem `break`. É exatamente "esgotou os passos sem concluir" — sem precisar de variável de controle.

O **`finally`**: as três métricas de resumo são registradas em qualquer saída — sucesso, erro do modelo ou passos esgotados. Se você registrasse só no caminho feliz, as execuções ruins sumiriam das estatísticas, e são justamente elas que você precisa ver.

## Quando métrica não basta

Agora o limite honesto deste módulo.

Métrica é agregada. Ela responde "os agentes estão dando mais voltas que ontem?" com precisão e por um custo baixo. Ela **não** responde "por que *esta* tarefa aqui deu doze voltas?".

Para essa pergunta você precisa de **trace**: o registro de uma execução específica, com cada passo, cada prompt, cada resposta e cada chamada de ferramenta em ordem, com seus tempos. É outra ferramenta — OpenTelemetry tracing, com Jaeger, Tempo ou equivalente — e está fora do escopo deste curso.

A divisão de trabalho, na prática:

| Pergunta | Ferramenta |
|---|---|
| Os agentes estão dando mais voltas que ontem? | métrica |
| Quanto custou o dia? Vai estourar o orçamento? | métrica |
| A ferramenta de banco ficou lenta? | métrica |
| Por que esta tarefa específica deu doze voltas? | trace |
| O que o modelo respondeu no passo 7? | trace ou log |
| A resposta final estava certa? | avaliação offline |

O erro comum é tentar resolver tudo com uma ferramenta só. Métrica com cardinalidade alta — `task_id` como label, por exemplo — é o jeito mais rápido de derrubar um Prometheus, e ainda assim não daria o que um trace dá.

Comece por métrica: é barata, agrega bem, e responde as perguntas de produção que aparecem primeiro. Acrescente trace quando a pergunta virar "por que esta execução aqui".

## Fechando o módulo

Nada neste módulo era uma ferramenta nova. Foi `Histogram`, `Counter`, `rate`, `histogram_quantile`, `predict_linear` e `for` — tudo que você já usava nos módulos anteriores, aplicado a um domínio onde a latência tem cauda longa, cada requisição custa dinheiro e uma falha pode voltar com status 200.

Agente é software. Observar agente é observabilidade. O que muda são os números que valem a pena olhar.
