# Auditoria 2026 — prometheus-curso-monitoring

Levantamento do estado do curso antes da atualização. **Nenhuma lição foi alterada.**

- Data da auditoria: 19/09/2026
- Commit auditado: `a3c333b` (último commit do repo: 25/01/2022)
- Escopo: 38 arquivos `.md`, 8 arquivos de configuração, 5 scripts Python, 24 imagens

Método: versões e flags foram conferidas baixando e executando os binários e consultando a API do GitHub e os índices Helm oficiais. Nada aqui foi escrito de memória. O que não deu para verificar está marcado como **[não verificado]**.

---

## 1. Resumo

| | |
|---|---|
| Lições sem problema | 6 de 38 |
| Lições que precisam só de bump de versão | 7 |
| Lições com algo depreciado ou removido | 11 |
| Lições com bug que **quebra o lab** | 9 |
| Lições com erro conceitual/factual | 5 |
| Imagens quebradas no GitHub | 14 de 24 |
| Links do README quebrados no GitHub | 11 |

O curso envelheceu melhor do que a idade sugere. A parte conceitual (modelo de dados, tipos de métrica, PromQL, golden signals, filosofia de alertas, baselines, z-score) continua correta e é a maior parte do valor. O que quebrou está concentrado em três lugares: **versões e URLs de download**, **caminhos absolutos de imagem/link**, e **flags que hoje precisam ser habilitadas explicitamente**.

---

## 2. Versões de referência (verificadas em 19/09/2026)

| Componente | No curso | Atual | Como verifiquei |
|---|---|---|---|
| Prometheus | 2.23.0 | **3.14.0** | GitHub releases API + binário baixado |
| Alertmanager | 0.21.0 | **0.34.1** | GitHub releases API |
| Grafana | 7.x (chart `7.4.5`) | **13.2.2** | GitHub releases API |
| node_exporter | (glob `v*`) | **1.12.1** | GitHub releases API |
| blackbox_exporter | sem tag | **0.28.0** | GitHub releases API |
| pushgateway | sem tag | **1.11.3** | GitHub releases API |
| mtail | 3.0.0-rc44 | **3.0.8** | GitHub releases API |
| cAdvisor | sem tag | **0.60.6** | GitHub releases API |
| kind | 0.10.0 | **0.33.0** | GitHub releases API |
| kind node image | `kindest/node:v1.21.1` | **`v1.37.0`** (também 1.34–1.36) | release notes do kind 0.33.0 |
| chart `prometheus-community/prometheus` | — | **1.43.3** (app 3.14.0) | `index.yaml` do repo |
| chart `kube-prometheus-stack` | não usado | **91.4.1** (app 0.94.0) | `index.yaml` do repo |
| chart `grafana/grafana` | — | **10.5.15** (app 12.3.1) | `index.yaml` do repo |

> Nota: o chart do Grafana ainda entrega app **12.3.1**, enquanto o release do Grafana já está em **13.2.2**. Vale registrar as duas nos labs para não confundir quem comparar.

### Mudanças estruturais do Prometheus 3.x que afetam o curso

Todas verificadas rodando o binário 3.14.0:

1. **O tarball não traz mais `consoles/` nem `console_libraries/`.** Conteúdo: `prometheus`, `promtool`, `prometheus.yml`, `LICENSE`, `NOTICE`. Os passos de `cp -r consoles /etc/prometheus` e as flags `--web.console.*` na unit do systemd viraram passo morto.
2. **`--storage.tsdb.retention.time` e `--storage.tsdb.retention.size` estão `[DEPRECATED]`.** O lugar hoje é o arquivo de configuração, em `storage.tsdb.retention.{time,size}` (validado com `promtool check config`).
3. **Nomes de métrica aceitam UTF-8**, com a sintaxe entre aspas: `sum({"minha.metrica.total"})` (validado com `promtool check rules`).
4. **Flags novas relevantes para o curso**: `--config.auto-reload`, `--web.enable-otlp-receiver` (ingestão OTLP nativa), remote write v2, agent mode.
5. **O `prometheus.yml` de exemplo mudou**: agora traz `scrape_native_histograms: true` e uma label `app: prometheus` no job.
6. **A UI web foi reescrita.** A antiga só volta com `--enable-feature=old-ui`.

---

## 3. Bloqueadores — labs que **não rodam** como estão escritos

Estes não são detalhe de versão, são passos que falham. Testados contra o Prometheus 3.14.0 real.

| # | Onde | O que acontece |
|---|---|---|
| B1 | `08_advanced_topics/02_management_api.md` | `curl -d POST localhost:9090/-/reload` responde **`Lifecycle API is not enabled.`** A lição nunca menciona `--web.enable-lifecycle`. O mesmo vale para `/-/quit`. |
| B2 | `04_quering/05_api_http.md` | `delete_series` responde **`{"status":"error",...,"error":"admin APIs disabled"}`**. Falta `--web.enable-admin-api`. Idem `clean_tombstones`. |
| B3 | `07_kubernetes/03_alerting_k8s.md` | `curl http://localhost:9090/-/reload` — mesmo problema do B1, e ainda é GET onde precisa ser POST. |
| B4 | `07_kubernetes/prometheus/alerting-codex.yml` | Usa `{{ $prometheusJob }}` e `{{ $namespace }}` em 10 lugares. Essas variáveis **não existem** em lugar nenhum do chart nem dos values. O `helm upgrade` da lição 07/03 quebra com "undefined variable". Sobra de copy/paste do kube-prometheus. |
| B5 | `02_install_prometheus/01_install_prometheus_linux.md` | Box `ubuntu/trusty64` = Ubuntu 14.04, fora de suporte desde 2019. E os passos de `consoles/` copiam diretórios que não existem mais no tarball 3.x. |
| B6 | `05_exporters/02_node_exporter.md` | A URL de download tem glob literal: `.../releases/download/v*/node_exporter-*.*-amd64.tar.gz` → **404**. `wget` não expande glob. |
| B7 | `05_exporters/03_mtail_exporter.md` | O nome do artefato mudou: era `mtail_3.0.0-rc44_Linux_x86_64.tar.gz`, hoje é **`mtail_3.0.8_linux_amd64.tar.gz`** (minúsculo, `amd64`). O `wget` da lição baixa uma versão de 2019. |
| B8 | `02_install_prometheus/03_install_grafana.md` | `apt-key add` foi removido do Ubuntu 22.04+ e o repo `packages.grafana.com/enterprise/deb` saiu do ar (**404**). Hoje é chave em `/etc/apt/keyrings/grafana.asc` + repo `https://apt.grafana.com`. |
| B9 | `07_kubernetes/01…04` | `kind` 0.10.0 e `kindest/node:v1.21.1` são de 2021. A 0.33.0 nem publica mais imagem 1.21. |

---

## 4. Tabela por lição

Legenda: ✅ ok · 🔢 bump de versão · ⚠️ depreciado/mudou · 🐞 bug que quebra o lab · 🧠 erro conceitual · ✏️ typo/link

### 01 — Introdução

| Lição | Status | O que mudar |
|---|---|---|
| `01_introducao.md` | ✅ 🔢 | Texto correto. Só vale citar que hoje é CNCF graduated e série 3.x, e uma linha sobre OTLP. |
| `02_apresentacao_intrutor.md` | ⚠️ | **Precisa de ti.** Bio de 2021: "gerente técnico do time de SRE na Azion". Não vou inventar bio nova — me passa o texto atualizado (Unisinos + IA aplicada). |
| `03_arquitetura_prometheus.md` | 🧠 | Cita **`promctl`**, que não existe. É `promtool` (e `amtool` do lado do Alertmanager). Vale acrescentar OTLP como caminho de entrada. |
| `04_alertmanager.md` | ✏️ ⚠️ | Sem `#` de título (único arquivo assim — quebra a consistência). "Pagerdutty" → "PagerDuty". Lista de integrações cresceu (Teams, Discord, Telegram, Webex, Jira). |

### 02 — Instalando o ambiente

| Lição | Status | O que mudar |
|---|---|---|
| `01_install_prometheus_linux.md` | 🐞 🔢 | B5. Prometheus 2.23.0 → 3.14.0; box trusty64 → 24.04; remover bloco `consoles`/`console_libraries` e as flags da unit; `apt-get install systemd` é inócuo mas sobra. |
| `02_install_alertmanager_linux.md` | 🔢 | Alertmanager 0.21.0 → 0.34.1. Resto do procedimento continua válido. |
| `03_install_grafana.md` | 🐞 ⚠️ | B8. Além do repo apt, os caminhos de menu mudaram: `Configurações → Data Source` hoje é `Connections → Data sources`; `Create → Dashboard` hoje é `Dashboards → New → Add visualization`. **4 screenshots para retirar** (ver §6). |
| `04_criando_alertas.md` | ✅ | Testei `promtool check rules` no 3.14: saída idêntica à da lição. Nada a mudar. |
| `05_prometheus_confs_avancadas.md` | ⚠️ 🧠 | `--storage.tsdb.retention.*` depreciado → mover para o arquivo de config. Diz que `evaluation_interval` tem default 15s — o default real é **1 minuto** (15s é só o que o arquivo de exemplo coloca). Vale citar `--config.auto-reload` e o receiver OTLP. |
| `06_docker.md` | 🔢 ⚠️ | `docker-compose` → `docker compose`. Imagens sem tag (`prom/prometheus`) — pinar. Depende do repo externo `cirolini/prometheus-lab`, que **não foi auditado aqui** e precisa do mesmo tratamento. |

### 03 — Conceitos

| Lição | Status | O que mudar |
|---|---|---|
| `01_modelo_de_dados.md` | ✅ ⚠️ | Conteúdo correto e continua valendo. Acrescentar nota curta sobre nomes de métrica em UTF-8 no Prometheus 3. |
| `02_tipos_de_metricas.md` | ✅ ⚠️ ✏️ | Os 4 tipos continuam certos. Falta **native histograms**, que é a mudança mais relevante do 3.x para esse tópico. "Sumary" → "Summary" (3 ocorrências). |
| `03_jobs_instances.md` | ✏️ | "scrap" → "scrape". O YAML de exemplo tem indentação inconsistente e três `- targets:` separados onde um só com três entradas seria mais claro. |

### 04 — Querying

| Lição | Status | O que mudar |
|---|---|---|
| `01_basico.md` | ✅ ⚠️ | Correto. Falta o modificador **`@`** (existe desde a 2.25) junto do `offset`, e a sintaxe UTF-8 entre aspas. |
| `02_operator.md` | ✅ | Correto. Opcional: `bottomk`, `quantile`, `count_values`, e vector matching (`on`/`ignoring`/`group_left`) — hoje não aparecem. |
| `03_functions.md` | 🧠 🐞 | **"O rate calcula a média por segundo de um _gauge_"** — errado, `rate()` é para **counters**. Link interno quebrado: aponta `03_conceitos/02_tipos_de_metricas.md` sem o `../`. Vale citar `histogram_quantile` com native histograms. |
| `04_recording_rules.md` | ✏️ | Título "Recoding Rules" → "Recording Rules". Conteúdo correto. |
| `05_api_http.md` | 🐞 | B2 — os exemplos de `delete_series`/`clean_tombstones` falham sem `--web.enable-admin-api`. Falta o parâmetro `limit` da query API. |

### 05 — Exporters

| Lição | Status | O que mudar |
|---|---|---|
| `01_introduction.md` | ✅ ✏️ | "scrap" → "scrape". Lista de exporters continua válida. |
| `02_node_exporter.md` | 🐞 🧠 | B6 (URL 404). E `chown node_exporter:node_exporter /usr/local/node_exporter` aponta para **caminho errado** — o binário foi para `/usr/local/bin/node_exporter`. |
| `03_mtail_exporter.md` | 🐞 🔢 | B7. O mtail está vivo (último push 03/2026, v3.0.8) — a lição continua fazendo sentido, só o download e o nome do artefato mudaram. |
| `04_pushgateway.md` | ✅ ✏️ | Conteúdo correto. "Proto" → "Pronto". Pinar `prom/pushgateway:v1.11.3`. |
| `05_blackbox_exporter.md` | ✏️ | Imagem com caminho absoluto (quebrada no GitHub). Pinar a imagem do container. Conteúdo correto. |
| `06_cadivisor.md` | ✏️ 🐞 | Nome do arquivo com typo. Imagem absoluta. Backtick solto em `prom/blackbox-exporter:master\``. YAML do job com indentação quebrada. cAdvisor via `/var/lib/docker` **não funciona no Docker Desktop do Mac** — precisa de aviso, já que tu usas Mac. |
| `07_escrevendo_exporters.md` | ⚠️ ✏️ | "primeito" → "primeiro". Backtick solto no fim. `virtualenv` → `python3 -m venv`. **`pip install uwsgi` compila e costuma falhar** em Python moderno/macOS — trocar por `start_http_server()` do `prometheus_client`, que é mais simples e é o caminho recomendado hoje. |

### 06 — Alerting

| Lição | Status | O que mudar |
|---|---|---|
| `01_criando_alertas.md` | ✅ ⚠️ | Expressões corretas. Os exemplos carregam labels internos antigos (`app!~"ltc\|pms"`) que não significam nada para quem lê — limpar. |
| `02_predict_linear.md` | 🧠 | Usa `node_filesystem_files_free`, que é **inode livre**, mas o texto fala em "espaço em disco". Para espaço é `node_filesystem_avail_bytes`. Imagem com caminho absoluto. |
| `03_notificando_email.md` | ⚠️ 🐞 | **`match:` está depreciado** desde o Alertmanager 0.22 → `matchers:`. O segundo YAML tem `receivers:` aninhado dentro de `route:` (indentação errada, não carrega). Gmail hoje exige app password. |
| `04_integrando_slack.md` | ⚠️ ✏️ | `match:` depreciado (idem). Aspas solta em `to: oncall@yourorganization.com'`. Rota `match: severity: email` é confusa. Caminho do Slack mudou: hoje é criar um app em `api.slack.com/apps` → Incoming Webhooks. Screenshot externa hospedada no grafana.com é de outra era — **retirar**. 2 imagens com caminho absoluto. |
| `05_silence.md` | ✏️ | 3 imagens com caminho absoluto. Conteúdo correto. Vale citar `amtool silence add` como alternativa via CLI. |

### 07 — Kubernetes

| Lição | Status | O que mudar |
|---|---|---|
| `01_install_prometheus_on_k8s.md` | 🐞 🧠 🔢 | B9. `port-forward` do **Alertmanager na porta 9090** (é 9093). Backtick solto no `helm install`. `helm show values ... >> values.yml` usa append onde queria `>`. E **"persistent volume externo, algo como um ELB na AWS"** — ELB é load balancer; para volume é **EBS**. |
| `02_install_grafana_on_k8s.md` | 🐞 | `kubectl port-forward grafana-... 9090` — Grafana é **3000**. Chart `grafana/grafana` hoje 10.5.15. |
| `03_alerting_k8s.md` | 🐞 | B3 + B4. Esta é a lição mais quebrada do módulo: o `helm upgrade` não completa. |
| `04_service_discovery.md` | 🐞 ✏️ | Título "PRometheus". `curl localhost:300/metrics` — falta um zero. As annotations `prometheus.io/scrape` são específicas do chart `prometheus`; com `kube-prometheus-stack` o caminho é ServiceMonitor/PodMonitor — precisa de nota. |
| `prometheus/values.yml` (1734 linhas) | ⚠️ | Dump do chart de 2021. `alertmanager v0.21.0`, `prometheus v2.26.0`, `configmap-reload v0.5.0`. Regerar. |
| `prometheus/values_simple.yml` (832 linhas) | ⚠️ | Idem (`v2.24.0`, `v0.21.0`). |
| `grafana/values.yml` (709 linhas) | ⚠️ | Dump de 2021: `tag: 7.4.5`, sidecar `1.10.7`, busybox `1.31.1`. Regerar. |

### 08 — Aspectos avançados

| Lição | Status | O que mudar |
|---|---|---|
| `01_federation.md` | ✅ ✏️ | Config correta e ainda válida. Typo: "parâmetro `math`" → `match`. Vale uma nota de que hoje, para visão global, `remote_write` + Thanos/Mimir costuma ser a escolha. |
| `02_management_api.md` | 🐞 🧠 | B1. Além disso os textos de resposta mudaram: hoje é **"Prometheus Server is Healthy."** e **"Prometheus Server is Ready."** (a lição diz "Prometheus is Healthy."). E `curl -d POST` manda "POST" **no corpo** — o certo é `-X POST`. |
| `03_baselines.md` | ✅ | Conteúdo original teu e continua correto. Só as 2 imagens com caminho absoluto. |
| `04_anomaly_detection.md` | 🐞 ✏️ | **O alerta está com o sinal errado**: `expr: (...) < 3`, mas a descrição diz "Z-Score is above than -3" e a explicação fala em -3. Deve ser `< -3`. Nome do alerta "HHTTP". Link `towardsdatascience.com` **404**. 2 imagens com caminho absoluto. |

### 09 — Conclusão

| Lição | Status | O que mudar |
|---|---|---|
| `01_modelos_de_monitoracao.md` | 🧠 ✏️ | `histogram_quantile(0.95, rate(...[10m]))` **sem `by (le)`** no primeiro exemplo (o do alerta, mais abaixo, está certo). Texto diz "o gráfico acima" 4 vezes mas **não há imagem nenhuma** no módulo. Backticks duplos sobrando em 4 inline codes. Link do SRE book migrou para `sre.google`. |
| `02_alerting_on_sitoms.md` | ✏️ | Nome do arquivo com typo (`sitoms`). Sem título `#`. Vários typos no corpo: "throbleshotting" (2x), "passeiveis", "prossivel", "estrair", "previnir", "usuario", "necessario". O conteúdo em si é ótimo e não precisa de reescrita. |
| `03_conclusion.md` | ✅ | Ok. Só vai precisar mencionar o módulo 10 quando ele existir. |

---

## 5. README

| Problema | Detalhe |
|---|---|
| 11 links quebrados no GitHub | Linhas 54–68 usam caminho **absoluto** (`](/07_kubernetes/...)`). No GitHub isso resolve para `github.com/07_kubernetes/...` e dá 404. Os módulos 01–06 usam caminho relativo e funcionam. Correção: tirar a `/` inicial. |
| Sem resumo em inglês | A ser adicionado na Fase 4. |
| Sem indicação de pré-requisitos, tempo estimado ou versões cobertas | — |

---

## 6. Imagens

**14 das 24 imagens estão quebradas no GitHub** — e nenhuma por arquivo faltando. Os arquivos estão todos no repo; o problema é que são referenciadas com caminho absoluto (`![x](/05_exporters/images/blackbox.png)`), que o GitHub resolve para a raiz do site. Módulos 01 e 02 usam caminho relativo e renderizam certo.

Arquivos afetados: `05_exporters/05`, `05_exporters/06`, `06_alerting/02`, `06_alerting/04` (2), `06_alerting/05` (3), `07_kubernetes/02`, `07_kubernetes/03`, `08_advanced_topics/03` (2), `08_advanced_topics/04` (2).

Correção: trocar por caminho relativo (`images/blackbox.png`). É uma linha por imagem e conserta as 14 de uma vez.

### Screenshots que **preciso que tu retire de novo** (não vou falsificar)

| Imagem | Por quê |
|---|---|
| `02_install_prometheus/images/grafana_login.png` | Tela de login do Grafana 7 vs 13 |
| `02_install_prometheus/images/grafana_datasource.png` | Menu mudou (`Connections → Data sources`) |
| `02_install_prometheus/images/grafana_grafico.png` | Editor de painel foi redesenhado |
| `07_kubernetes/images/grafana_k8s.png` | Idem |
| `06_alerting/images/alertmanager-silence{1,2,3}.png` | UI do Alertmanager mudou entre 0.21 e 0.34 |
| `06_alerting/images/alertmanager_slack{,2}.png` | Layout de mensagem do Slack mudou |
| externa: `grafana.com/.../AlertmanagerWebHooks.png` | Screenshot de terceiro, UI antiga do Slack — sugiro remover em vez de substituir |
| `02_install_prometheus/images/prom_*.png` (4) | UI do Prometheus foi **reescrita** na 3.x |
| `07_kubernetes/images/prometheus_alerting.png` | Idem |

As que **continuam válidas**: `prom_architecture.png` (diagrama oficial, conferir se a versão nova do site já difere), `linear_regression.png`, `z-score.png`, `z-score-formula.png`, `baseline.png`, `baseline_avg.png`, `blackbox.png`, `cadvisor.png` (essas últimas duas com UI um pouco antiga, mas legíveis).

---

## 7. Nomes de arquivo/pasta com typo

| Atual | Sugestão |
|---|---|
| `04_quering/` | `04_querying/` |
| `05_exporters/06_cadivisor.md` | `06_cadvisor.md` |
| `09_conclusion/02_alerting_on_sitoms.md` | `02_alerting_on_symptoms.md` |
| `01_introducao/02_apresentacao_intrutor.md` | `02_apresentacao_instrutor.md` |

⚠️ Renomear pasta **quebra links externos**: o repo tem 385 estrelas e 123 forks, e é provável que existam posts e favoritos apontando para `/04_quering/`. Ver §9.

---

## 8. Higiene do repositório

| Item | Observação |
|---|---|
| `05_exporters/my_exporter/__pycache__/app.cpython-39.pyc` | Bytecode do Python 3.9 versionado. Remover e criar `.gitignore` (o repo **não tem um**). |
| `05_exporters/my_exporter/deploy.yml` | É um **GitHub Actions workflow** solto dentro de uma pasta de lição. Não está em `.github/workflows`, então nunca rodou. Faz push para `azionedge/base-model:latest` e usa `secrets.DOCKERHUB_*`. É conteúdo do teu empregador anterior, que tu marcou como fora de escopo — **sugiro apagar**. Actions `v1`/`v2` também estão obsoletas. |
| `05_exporters/my_exporter/app_v{1..4}.py` | Não referenciados por nenhuma lição. A lição 07 mostra o código inline. Vale decidir se viram o lab de verdade ou saem. |
| Sem `.gitignore`, sem `LICENSE`, sem `CHANGELOG.md` | Para um repo com 385 estrelas, a **licença** é a falta mais séria — sem ela ninguém sabe se pode usar o material. |

---

## 9. Decisões que precisam do teu ok

Não mexo em nada disso sem tu responder:

1. **Renomear as pastas/arquivos com typo?** Conserta o nome mas quebra links externos de terceiros para um repo com 123 forks. Alternativa: renomear e deixar um `README.md` stub na pasta antiga apontando para a nova.
2. **Trocar o módulo 07 de `prometheus-community/prometheus` para `kube-prometheus-stack`?** O teu plano cita o kube-prometheus-stack, mas as lições atuais usam o chart antigo. Trocar é o caminho certo em 2026 (é o que todo mundo usa), mas **reescreve o módulo 07 inteiro**: o service discovery por annotation vira ServiceMonitor, e os arquivos de alerta viram PrometheusRule. Isso é mudança de estrutura, não conserto.
3. **Bio do instrutor** — me passa o texto novo (Unisinos, IA aplicada). Não vou escrever por ti.
4. **`deploy.yml` do Azion** — apago?
5. **Licença** — qual? Para curso, CC BY-SA 4.0 no texto + MIT nos códigos é o par mais comum.
6. **`cirolini/prometheus-lab`** (repo externo usado na lição 02/06) — a Fase 1 cria `labs/` aqui dentro. O `prometheus-lab` vira redundante: aposento a referência, ou mantenho os dois?

---

## 10. Limitações desta auditoria

Para não te dar falsa confiança:

- **No momento da auditoria esta máquina não tinha `docker`, `kind`, `helm` nem `kubectl`.** Por isso os achados do módulo 07 (B3, B4, B9 e a tabela de values) são **análise estática**, não execução. Os bloqueadores B1 e B2 e todo o comportamento do Prometheus 3.x eu validei baixando e executando o binário `prometheus-3.14.0.darwin-arm64` localmente.
- **Ambiente resolvido em 19/09/2026, depois da auditoria** (via Homebrew, a pedido): `kind 0.33.0`, `kubectl 1.37.0`, `helm 4.3.0`, docker CLI 29.8.1 + compose 5.5.1, runtime `colima 0.10.3` (macOS Virtualization.Framework, 4 CPU / 8 GB / 60 GB, docker server 29.5.2). `docker run hello-world` e `helm search repo` confirmados. **A regra 4 do plano passa a ser cumprível a partir da Fase 1** — os achados do módulo 07 ainda precisam ser confirmados rodando.
  - Nota de percurso: o `colima start` falhou duas vezes com `SHA512 checksum mismatch` na imagem de VM. Diagnóstico: o upstream serve 332.354.401 bytes e a transferência chegava truncada (`gzip -t` → `unexpected end of file`), em pontos diferentes a cada tentativa — daí hashes diferentes. **Não foi adulteração; a verificação do colima funcionou.** Resolvido refazendo o download com `curl -C -` até completar e conferindo o SHA512 contra o valor publicado no próprio binário do colima antes de usar. A verificação não foi contornada.
- **`github.com/cirolini/prometheus-lab` não foi auditado** (está fora deste repo). Se ele continuar sendo citado, tem a mesma dívida de versão.
- Itens marcados **[não verificado]**: nenhum nesta rodada — tudo que afirmei acima foi checado. Onde não tive como checar (labs k8s), está dito explicitamente que é análise estática.

---

## 11. Sugestão de ordem para as próximas fases

Independente do que tu decidir em §9, a ordem que rende mais por esforço:

1. **Correções de 10 minutos que destravam o repo hoje**: os 11 links do README e as 14 imagens com caminho absoluto. É achar-e-trocar, zero risco, e conserta a primeira impressão de quem chega pelo perfil.
2. **Bloqueadores B1–B9** — são o que faz alguém desistir no meio do curso.
3. **Erros conceituais** (rate/gauge, ELB/EBS, promctl, inodes, z-score `< -3`, `by (le)`) — são poucos, mas é o tipo de coisa que alguém cita de volta pra ti.
4. Aí sim Fase 1 (`labs/`), Fase 2 (versões e notas do ecossistema), Fase 3 (módulo 10), Fase 4 (README/CHANGELOG).
