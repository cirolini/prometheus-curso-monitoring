"""App de exemplo do modulo 10: uma chamada de LLM instrumentada.

Sobe junto com o lab (`make up`) e expoe /metrics como qualquer outra
aplicacao do curso. Por padrao usa um provider simulado, entao roda sem
chave de API nenhuma.
"""
from __future__ import annotations

import os
import time

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel
from starlette.responses import PlainTextResponse, Response

import metrics as m
from agent import run_agent
from provider import ProviderError, build_provider

app = FastAPI(title="LLM app instrumentada", docs_url="/docs")
provider = build_provider()

# Preco por milhao de tokens. Coloque aqui o preco do SEU provider - este
# numero nao vem de lugar nenhum magico, e' voce que mantem.
PRICE_IN = float(os.getenv("LLM_PRICE_INPUT_PER_MTOK", "3.0"))
PRICE_OUT = float(os.getenv("LLM_PRICE_OUTPUT_PER_MTOK", "15.0"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))

# Erros que vale a pena tentar de novo. Um 400 nao entra aqui: tentar de
# novo so' gasta dinheiro para receber o mesmo 400.
RETRIABLE = {"rate_limit", "timeout", "server_error", "connection_error"}


class AskRequest(BaseModel):
    prompt: str = "oi"


def call_llm(prompt: str):
    """Uma chamada, com retry e instrumentada em todas as saidas."""
    attempt = 0
    started = time.perf_counter()
    m.inflight.labels(provider.name).inc()
    try:
        while True:
            try:
                completion = provider.complete(prompt)
            except ProviderError as e:
                m.errors_total.labels(provider.name, provider.model, e.error_type).inc()
                if e.error_type in RETRIABLE and attempt < MAX_RETRIES:
                    attempt += 1
                    m.retries_total.labels(provider.name, provider.model, e.error_type).inc()
                    time.sleep(0.2 * (2 ** attempt))  # backoff exponencial
                    continue
                # Mede a duracao tambem no fracasso. Se voce so' medir o
                # caminho feliz, a latencia fica bonita justamente quando o
                # sistema esta' ruim.
                m.operation_duration.labels(
                    "chat", provider.name, provider.model, "error"
                ).observe(time.perf_counter() - started)
                raise

            elapsed = time.perf_counter() - started
            labels = ("chat", provider.name, provider.model)
            m.operation_duration.labels(*labels, "ok").observe(elapsed)
            m.token_usage.labels(*labels, "input").observe(completion.input_tokens)
            m.token_usage.labels(*labels, "output").observe(completion.output_tokens)
            m.tokens_total.labels(provider.name, provider.model, "input").inc(
                completion.input_tokens
            )
            m.tokens_total.labels(provider.name, provider.model, "output").inc(
                completion.output_tokens
            )
            cost = (
                completion.input_tokens / 1_000_000 * PRICE_IN
                + completion.output_tokens / 1_000_000 * PRICE_OUT
            )
            m.cost_usd_total.labels(provider.name, provider.model).inc(cost)
            return completion, elapsed, cost, attempt
    finally:
        m.inflight.labels(provider.name).dec()


@app.post("/ask")
def ask(req: AskRequest):
    try:
        completion, elapsed, cost, retries = call_llm(req.prompt)
    except ProviderError as e:
        # 503 de proposito: a falha e' do provider, nao do cliente.
        return Response(
            content=f'{{"error":"{e.error_type}"}}',
            status_code=503,
            media_type="application/json",
        )
    return {
        "text": completion.text,
        "model": completion.model,
        "input_tokens": completion.input_tokens,
        "output_tokens": completion.output_tokens,
        "duration_seconds": round(elapsed, 3),
        "estimated_cost_usd": round(cost, 6),
        "retries": retries,
    }


@app.post("/agent")
def agent(req: AskRequest):
    return run_agent(provider, req.prompt)


@app.get("/health")
def health():
    return {"status": "ok", "provider": provider.name, "model": provider.model}


@app.get("/metrics")
def prometheus_metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
