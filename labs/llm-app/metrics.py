"""Metricas do app de IA.

Os nomes seguem as convencoes de GenAI do OpenTelemetry, traduzidas para o
estilo do Prometheus (ponto vira underline). A spec esta em
https://github.com/open-telemetry/semantic-conventions-genai e, na data em
que isto foi escrito (19/09/2026), TUDO nela ainda esta marcado como
"Development" - ou seja, pode mudar.

Uma coisa que a spec NAO define: custo. Nao existe metrica de custo nas
convencoes. Entao `llm_cost_usd_total` e' invencao nossa, e esta de
proposito com prefixo diferente para deixar claro o que e' padrao e o que
e' caseiro.
"""
from prometheus_client import Counter, Gauge, Histogram

# --- Duracao da chamada -----------------------------------------------------
# gen_ai.client.operation.duration na spec. Os buckets vao ate 60s porque
# chamada de LLM tem cauda longa: o p50 pode ser 1s e o p99 passar de 30s.
# Usar os buckets default do prometheus_client aqui daria um p99 inutil.
operation_duration = Histogram(
    "gen_ai_client_operation_duration_seconds",
    "Duracao da chamada ao modelo",
    ["gen_ai_operation_name", "gen_ai_provider_name", "gen_ai_request_model", "outcome"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60),
)

# --- Tokens -----------------------------------------------------------------
# gen_ai.client.token.usage. A spec manda um histograma unico com a label
# gen_ai.token.type = input|output, e nao duas metricas separadas.
token_usage = Histogram(
    "gen_ai_client_token_usage_tokens",
    "Tokens consumidos por chamada",
    ["gen_ai_operation_name", "gen_ai_provider_name", "gen_ai_request_model", "gen_ai_token_type"],
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 100000),
)

# Counter separado para somar tokens ao longo do tempo. O histograma acima
# responde "como e' a distribuicao"; este responde "quantos no total".
tokens_total = Counter(
    "gen_ai_client_tokens_total",
    "Total acumulado de tokens",
    ["gen_ai_provider_name", "gen_ai_request_model", "gen_ai_token_type"],
)

# --- Custo (nao padronizado) ------------------------------------------------
cost_usd_total = Counter(
    "llm_cost_usd_total",
    "Custo acumulado estimado em dolares",
    ["gen_ai_provider_name", "gen_ai_request_model"],
)

# --- Erros ------------------------------------------------------------------
# Separado por TIPO. Agregar erro de LLM num contador so' esconde o que
# importa: rate limit se resolve com backoff, timeout as vezes so' precisa
# de paciencia, e erro de conteudo nao se resolve tentando de novo.
errors_total = Counter(
    "gen_ai_client_errors_total",
    "Erros por tipo",
    ["gen_ai_provider_name", "gen_ai_request_model", "error_type"],
)

retries_total = Counter(
    "gen_ai_client_retries_total",
    "Tentativas extras feitas depois de uma falha",
    ["gen_ai_provider_name", "gen_ai_request_model", "error_type"],
)

inflight = Gauge(
    "gen_ai_client_requests_inflight",
    "Chamadas ao modelo em andamento",
    ["gen_ai_provider_name"],
)

# --- Agente (licao 5) -------------------------------------------------------
agent_duration = Histogram(
    "gen_ai_invoke_agent_duration_seconds",
    "Duracao de uma execucao completa do agente",
    ["gen_ai_agent_name", "outcome"],
    buckets=(0.5, 1, 2, 5, 10, 20, 45, 90, 180),
)

agent_inference_calls = Histogram(
    "gen_ai_invoke_agent_inference_calls",
    "Quantas chamadas ao modelo o agente fez numa execucao",
    ["gen_ai_agent_name"],
    buckets=(1, 2, 3, 5, 8, 12, 20, 30),
)

agent_tool_calls = Histogram(
    "gen_ai_invoke_agent_tool_calls",
    "Quantas ferramentas o agente chamou numa execucao",
    ["gen_ai_agent_name"],
    buckets=(0, 1, 2, 3, 5, 8, 12, 20),
)

tool_duration = Histogram(
    "gen_ai_execute_tool_duration_seconds",
    "Duracao da execucao de uma ferramenta",
    ["gen_ai_tool_name", "outcome"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

agent_steps_exhausted = Counter(
    "gen_ai_invoke_agent_steps_exhausted_total",
    "Execucoes que bateram no limite de passos sem terminar",
    ["gen_ai_agent_name"],
)
