# Convenções do OpenTelemetry para GenAI

Nos capítulos anteriores os nomes das métricas apareceram assim:

```
gen_ai_client_operation_duration_seconds
gen_ai_client_token_usage_tokens
```

Não inventei esses nomes. Eles vêm das **convenções semânticas de GenAI do OpenTelemetry**, e vale entender o que são, porque valem e — principalmente — onde elas ainda não chegaram.

## O que é uma convenção semântica

Convenção semântica é um acordo sobre **como chamar as coisas**. Se todo mundo que instrumenta uma chamada de LLM usar `gen_ai.client.token.usage` com a label `gen_ai.token.type`, então um dashboard funciona em qualquer stack, um alerta é portável, e a biblioteca que você instalar hoje fala a mesma língua do código que você escreveu no ano passado.

É o mesmo raciocínio das *best practices* de nomes que vimos no [módulo 03](../03_conceitos/01_modelo_de_dados.md), só que acordado por um comitê em vez de por costume.

## Onde a spec mora (e por que isso importa)

Aqui vai o primeiro aviso prático: **a spec de GenAI saiu do repositório principal do OpenTelemetry.** Ela vive hoje em um repositório próprio:

> https://github.com/open-telemetry/semantic-conventions-genai

Se você procurar em `open-telemetry/semantic-conventions`, vai encontrar uma página dizendo que o conteúdo mudou de lugar. Muito material na internet ainda aponta para o endereço antigo.

O segundo aviso é mais importante: **na data em que escrevo isto (setembro de 2026), tudo na spec de GenAI ainda está marcado como `Development`.** Não é release candidate, não é estável. O próprio repositório ainda não tem release publicado.

Na prática, isso significa:

- os nomes **podem mudar**, e já mudaram no passado
- use as convenções como guia, não como contrato
- escreva os seus dashboards de um jeito que você consiga renomear depois — recording rules ajudam muito aqui
- **confira a spec antes de instrumentar**, não confie neste capítulo daqui a um ano

Estou sendo explícito sobre isso porque é honesto: esta é a parte do curso que envelhece mais rápido.

## As métricas que a spec define

Do lado do **cliente** — a sua aplicação chamando um modelo, que é o caso da maioria:

| Métrica | Tipo | Unidade | O que é |
|---|---|---|---|
| `gen_ai.client.operation.duration` | Histogram | `s` | duração da chamada |
| `gen_ai.client.token.usage` | Histogram | `{token}` | tokens de entrada e saída |
| `gen_ai.client.operation.time_to_first_chunk` | Histogram | `s` | tempo até o primeiro pedaço, em streaming |
| `gen_ai.client.operation.time_per_output_chunk` | Histogram | `s` | tempo por pedaço depois do primeiro |

Do lado do **servidor** — se você *serve* um modelo, e não apenas consome:

| Métrica | Tipo | Unidade |
|---|---|---|
| `gen_ai.server.request.duration` | Histogram | `s` |
| `gen_ai.server.time_to_first_token` | Histogram | `s` |
| `gen_ai.server.time_per_output_token` | Histogram | `s` |

Repare numa sutileza: do lado do cliente a spec fala em **chunk**, do lado do servidor em **token**. Faz sentido — quem chama por HTTP recebe pedaços de stream e não sabe onde estão as fronteiras de token; quem roda o modelo sabe.

E as de **agente e ferramenta**, que vamos usar no capítulo 5:

| Métrica | Tipo | Unidade |
|---|---|---|
| `gen_ai.invoke_agent.duration` | Histogram | `s` |
| `gen_ai.invoke_agent.inference_calls` | Histogram | `{inference_call}` |
| `gen_ai.invoke_agent.tool_calls` | Histogram | `{tool_call}` |
| `gen_ai.execute_tool.duration` | Histogram | `s` |
| `gen_ai.invoke_workflow.duration` | Histogram | `s` |

## Os atributos

Os principais, com o nível de exigência que a spec dá:

| Atributo | Exigência | Exemplos |
|---|---|---|
| `gen_ai.operation.name` | obrigatório | `chat`, `generate_content`, `text_completion`, `invoke_agent`, `execute_tool`, `embeddings` |
| `gen_ai.provider.name` | obrigatório | `openai`, `gcp.gen_ai`, `gcp.vertex_ai` |
| `gen_ai.token.type` | obrigatório (na métrica de token) | `input`, `output` |
| `gen_ai.request.model` | condicional, se disponível | o modelo que você pediu |
| `gen_ai.response.model` | recomendado | o modelo que de fato respondeu |

Os dois últimos parecem redundantes e não são: você pede `modelo-x` e o provider pode te servir `modelo-x-0613`. Quando a latência muda sem você ter mexido em nada, essa diferença costuma ser a resposta.

## O buraco: custo

Agora a parte que interessa a qualquer pessoa que paga a conta.

**A spec não define nenhuma métrica de custo.** Nenhuma. Não é que esteja instável — não existe.

Faz algum sentido: o OpenTelemetry padroniza o que é observável no processo, e preço é contrato comercial, muda por fornecedor, por região, por acordo e por dia. Mas o resultado prático é que a métrica que mais interessa ao negócio é justamente a que você tem que inventar.

Foi o que fizemos:

```
llm_cost_usd_total    ← prefixo diferente, de propósito
```

A recomendação é essa: **use o prefixo `gen_ai_` só para o que a spec define**, e um prefixo seu para o resto. Assim, quando alguém olhar o seu `/metrics` daqui a dois anos, vai saber na hora o que é padrão e o que é decisão da casa.

## Do OpenTelemetry para o Prometheus

Os nomes da spec usam ponto: `gen_ai.client.token.usage`. Os nomes clássicos do Prometheus usam underline. Existem dois caminhos.

### Caminho 1: instrumentar direto com a biblioteca do Prometheus

Foi o que o lab fez. Você escreve o nome já traduzido:

```
gen_ai.client.token.usage   →   gen_ai_client_token_usage_tokens
```

Ponto vira underline e o sufixo da unidade entra no fim, seguindo a convenção do Prometheus. Simples, sem peça a mais na arquitetura, e é o caminho certo se você já é uma casa Prometheus.

### Caminho 2: OTLP direto no Prometheus

Aqui entra uma novidade que amarra com o [módulo 02](../02_install_prometheus/05_prometheus_confs_avancadas.md). O Prometheus 3 recebe métricas via OTLP nativamente:

```
--web.enable-otlp-receiver
```

Com isso, uma aplicação instrumentada com o SDK do OpenTelemetry empurra métricas direto para o Prometheus, sem collector no meio. O endpoint é `/api/v1/otlp/v1/metrics`.

E tem um detalhe bonito: como o Prometheus 3 aceita [nomes em UTF-8](../03_conceitos/01_modelo_de_dados.md), dá para **preservar os pontos** e consultar assim:

```
{"gen_ai.client.token.usage"}
```

Ou seja, o nome fica idêntico ao da spec, sem tradução. A configuração de como tratar os nomes que chegam por OTLP fica na seção `otlp` do arquivo de configuração.

Qual escolher? Se a sua casa é Prometheus e a instrumentação é sua, o caminho 1 é mais simples. Se você já tem OpenTelemetry na empresa, ou precisa mandar o mesmo dado para mais de um destino, o caminho 2 evita instrumentar duas vezes.

## O que levar

1. Use os nomes da spec onde ela define — de graça você ganha portabilidade
2. Trate-os como instáveis e **confira antes de instrumentar**
3. Custo é seu: prefixo próprio, e você mantém a tabela de preços
4. Não instrumente duas vezes só para ter os dois formatos

No próximo capítulo, os gráficos e alertas em cima de tudo isso.
