# Changelog

## Edição 2026

Primeira atualização grande desde janeiro de 2022. O curso foi escrito para o Prometheus 2.x e boa parte do ecossistema mudou de lugar desde então.

O levantamento completo que motivou cada mudança está em [`docs/audit-2026.md`](docs/audit-2026.md).

### Acrescentado

**Módulo 10 — Observando aplicações com IA.** Cinco lições sobre o que muda quando a aplicação chama um modelo de linguagem: latência de cauda longa, custo por requisição, tokens como unidade de trabalho, falhas que voltam com status 200, e como observar um agente que chama ferramentas em sequência. Inclui as convenções de GenAI do OpenTelemetry e o limite honesto de onde métrica para e trace começa.

**Labs que sobem com um comando.** `make up` levanta a stack inteira em Docker: Prometheus, Alertmanager, Grafana com datasource e dashboards provisionados, node_exporter, blackbox_exporter, pushgateway, cAdvisor, uma aplicação de exemplo e a aplicação de IA do módulo 10 (em modo simulado, sem precisar de chave). `make k8s` cria um cluster kind com o kube-prometheus-stack.

**Dois dashboards do Grafana** provisionados automaticamente: visão geral do lab e o do módulo 10.

**Um `.gitignore`**, que o repositório não tinha.

**Licenças.** O conteúdo passou a ser [CC BY-SA 4.0](LICENSE) e o código [MIT](LICENSE-CODE). Até aqui o repositório não tinha licença nenhuma, o que na prática deixava quem quisesse usar o material sem saber se podia.

### Atualizado

| | Era | Virou |
|---|---|---|
| Prometheus | 2.23.0 | **3.14.0** |
| Alertmanager | 0.21.0 | **0.34.1** |
| Grafana | 7.x | **13.2.2** |
| node_exporter | (sem versão) | **1.12.1** |
| blackbox_exporter | (sem tag) | **0.28.0** |
| pushgateway | (sem tag) | **1.11.3** |
| mtail | 3.0.0-rc44 | **3.0.8** |
| cAdvisor | (sem tag) | **0.55.1** |
| kind | 0.10.0 | **0.33.0** |
| Box do Vagrant | `ubuntu/trusty64` | `bento/ubuntu-24.04` |

**Módulo 07 reescrito para o kube-prometheus-stack** (chart 91.4.1). O curso usava o chart `prometheus-community/prometheus`, que ainda funciona mas quase ninguém usa hoje. Com o Prometheus Operator, o service discovery por annotation vira `ServiceMonitor`/`PodMonitor` e os arquivos de alerta viram `PrometheusRule`. Os values da edição antiga foram preservados em [`07_kubernetes/legacy/`](07_kubernetes/legacy/).

### Corrigido

**Coisas que quebravam o lab:**

- `/-/reload` e `/-/quit` respondiam `Lifecycle API is not enabled.` — faltava documentar `--web.enable-lifecycle`
- `delete_series` respondia `admin APIs disabled` — faltava `--web.enable-admin-api`
- a URL de download do node_exporter tinha curinga literal (`v*`) e dava 404
- o nome do artefato do mtail mudou de `Linux_x86_64` para `linux_amd64`
- o repositório apt do Grafana saiu do ar e o `apt-key` foi removido do Ubuntu 22.04+
- o tarball do Prometheus 3 não traz mais `consoles/` nem `console_libraries/`, e o curso mandava copiá-los
- `alerting-codex.yml` usava as variáveis `{{ $prometheusJob }}` e `{{ $namespace }}`, que não existiam em lugar nenhum do chart — o `helm upgrade` falhava com "undefined variable"

**Erros conceituais:**

- `rate()` estava descrito como "média por segundo de um *gauge*". É sobre **counter**
- `delta` aparecia aplicado a counter, onde o certo é `increase`
- o alerta de disco usava `node_filesystem_files_free`, que é **inode livre**, enquanto o texto falava em espaço. Para espaço é `node_filesystem_avail_bytes`
- o alerta de z-score comparava `< 3` enquanto a lição inteira explicava `-3`
- `histogram_quantile` aparecia sem `by (le)` em dois lugares, o que dá resultado errado em silêncio
- "persistent volume, algo como um **ELB**" — ELB é load balancer; volume na AWS é **EBS**
- `promctl` não existe; a ferramenta é `promtool`
- `evaluation_interval` estava documentado com default de 15s; o default real é 1 minuto

**Depreciações:**

- `match:` no Alertmanager está *deprecated* desde a 0.22 — todos os exemplos usam `matchers:`
- a retenção do Prometheus saiu das flags de inicialização para o arquivo de configuração
- a lição de escrever exporter mandava instalar `uwsgi`, que compila e falha em Python recente — trocado por `gunicorn`

**Links e imagens:**

- 11 links do sumário usavam caminho absoluto e davam 404 no GitHub
- 14 imagens tinham o mesmo problema — os arquivos estavam lá, mas o caminho resolvia para a raiz do site
- um link interno entre módulos apontava para o diretório errado
- referência a um artigo do `towardsdatascience.com` que saiu do ar
- o link do SRE book migrou para `sre.google`

### Removido

**15 screenshots desatualizadas.** Eram de interfaces que mudaram demais para o texto continuar batendo — Prometheus 2, Grafana 7, Alertmanager 0.21. Tirar é mais honesto do que deixar o aluno procurando na tela um botão que não existe mais. Os arquivos `.png` seguem no repositório, então é só voltar a referenciá-los se forem refeitos.

As imagens que continuam são as que ensinam e não envelhecem: o diagrama de arquitetura, a fórmula do z-score, os gráficos de baseline e de regressão linear, e as telas do blackbox e do cAdvisor.

**`05_exporters/my_exporter/deploy.yml`** — um workflow do GitHub Actions solto dentro de uma pasta de lição. Não estava em `.github/workflows`, então nunca rodou, e fazia push para um registry que não tem a ver com o curso.

### Renomeado

Com stub de redirect em cada nome antigo, para não quebrar links de terceiros:

| Antes | Agora |
|---|---|
| `04_quering/` | `04_querying/` |
| `05_exporters/06_cadivisor.md` | `06_cadvisor.md` |
| `09_conclusion/02_alerting_on_sitoms.md` | `02_alerting_on_symptoms.md` |
| `01_introducao/02_apresentacao_intrutor.md` | `02_apresentacao_instrutor.md` |

### Notas de ecossistema acrescentadas

Curtas, onde o assunto mudou de um jeito que importa para quem está aprendendo:

- **native histograms** (módulo 03) — buckets exponenciais automáticos, sem escolher bucket na mão
- **nomes em UTF-8** (módulo 03) — o Prometheus 3 aceita ponto no nome da métrica, com sintaxe entre aspas
- **modificador `@`** (módulo 04) — fixar a consulta num instante, em vez do `offset` relativo
- **ingestão OTLP** (módulos 02 e 10) — o Prometheus 3 recebe OpenTelemetry direto, sem collector
- **remote_write e Thanos/Mimir** (módulo 08) — alternativa ao federation para visão global

### Atualizado também

**A bio do instrutor** foi reescrita. A anterior era de 2021.

### Pendente

- **Screenshots novas.** As 15 antigas foram removidas e o texto foi escrito para funcionar sem elas. Se forem refeitas em algum momento, os arquivos originais continuam no repositório como referência do que cada uma mostrava
- **O lab do módulo 10 não foi executado ponta a ponta.** Foram validados as regras com `promtool`, a sintaxe do Python e o JSON do dashboard, mas o `make up` com a aplicação de IA ainda precisa ser rodado
