"""Adapter de provider - de proposito neutro.

O curso nao quer amarrar ninguem a um fornecedor, entao aqui existe uma
interface fina e duas implementacoes: `mock` (default, roda sem chave) e
`http` (chama um endpoint de chat que voce configura por variavel de
ambiente).

Trocar de fornecedor e' implementar `complete()`. O resto do app - e todas
as metricas - nao muda.
"""
from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass


@dataclass
class Completion:
    text: str
    input_tokens: int
    output_tokens: int
    model: str


class ProviderError(Exception):
    """Falha da chamada, ja classificada.

    O `error_type` e' o que vai virar label no Prometheus. Mantenha o
    conjunto de valores pequeno e estavel: label com cardinalidade alta
    (mensagem de erro crua, por exemplo) derruba o Prometheus.
    """

    def __init__(self, error_type: str, message: str = ""):
        self.error_type = error_type
        super().__init__(message or error_type)


class MockProvider:
    """Simula um LLM. Latencia de cauda longa, tokens e falhas plausiveis."""

    name = "mock"

    def __init__(self, model: str = "mock-model-1"):
        self.model = model

    def complete(self, prompt: str) -> Completion:
        # Lognormal porque latencia de LLM nao e' normal: a maioria das
        # chamadas e' rapida e uma minoria demora muito. E' justamente
        # essa cauda que faz media ser uma metrica ruim aqui.
        time.sleep(min(random.lognormvariate(-0.5, 0.9), 25))

        roll = random.random()
        if roll < 0.03:
            raise ProviderError("rate_limit", "429 do provider")
        if roll < 0.05:
            raise ProviderError("timeout", "estourou o tempo")
        if roll < 0.06:
            raise ProviderError("server_error", "5xx do provider")

        input_tokens = max(1, len(prompt.split()) + random.randint(20, 200))
        output_tokens = random.randint(30, 1200)
        return Completion(
            text=f"(resposta simulada para: {prompt[:40]})",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
        )


class HTTPProvider:
    """Chama um endpoint de chat real.

    Configurado inteiramente por ambiente, para o curso nao ter opiniao
    sobre qual fornecedor voce usa:

        LLM_PROVIDER=http
        LLM_BASE_URL=https://api.seu-provider.com/v1/chat/completions
        LLM_MODEL=nome-do-modelo
        LLM_API_KEY=...
        LLM_AUTH_HEADER=Authorization      # ou x-api-key, etc
        LLM_AUTH_PREFIX="Bearer "          # vazio se o provider nao usa

    O corpo e a leitura da resposta seguem o formato de chat mais comum.
    Se o seu provider usa outro, e' aqui que voce mexe - e so' aqui.
    """

    def __init__(self):
        self.name = os.getenv("LLM_PROVIDER_NAME", "custom")
        self.model = os.getenv("LLM_MODEL", "unknown")
        self.base_url = os.getenv("LLM_BASE_URL", "")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.auth_header = os.getenv("LLM_AUTH_HEADER", "Authorization")
        self.auth_prefix = os.getenv("LLM_AUTH_PREFIX", "Bearer ")
        self.timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

    def complete(self, prompt: str) -> Completion:
        import httpx

        headers = {"content-type": "application/json"}
        if self.api_key:
            headers[self.auth_header] = f"{self.auth_prefix}{self.api_key}"

        try:
            r = httpx.post(
                self.base_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                },
                timeout=self.timeout,
            )
        except httpx.TimeoutException as e:
            raise ProviderError("timeout", str(e)) from e
        except httpx.HTTPError as e:
            raise ProviderError("connection_error", str(e)) from e

        # Classificacao do erro. Repare que 429 e' seu proprio tipo: ele se
        # resolve com backoff, ao contrario de um 400, que vai falhar de novo
        # por mais que voce tente.
        if r.status_code == 429:
            raise ProviderError("rate_limit", r.text[:200])
        if r.status_code >= 500:
            raise ProviderError("server_error", r.text[:200])
        if r.status_code >= 400:
            raise ProviderError("client_error", r.text[:200])

        data = r.json()
        usage = data.get("usage", {})
        return Completion(
            text=_first_text(data),
            # Se o provider nao devolve contagem de token, nao invente:
            # zero e' honesto e aparece no grafico como zero.
            input_tokens=int(usage.get("input_tokens", usage.get("prompt_tokens", 0))),
            output_tokens=int(usage.get("output_tokens", usage.get("completion_tokens", 0))),
            model=data.get("model", self.model),
        )


def _first_text(data: dict) -> str:
    choices = data.get("choices") or []
    if choices:
        return (choices[0].get("message") or {}).get("content", "")
    content = data.get("content") or []
    if content and isinstance(content, list):
        return content[0].get("text", "")
    return ""


def build_provider():
    if os.getenv("LLM_PROVIDER", "mock").lower() == "http":
        return HTTPProvider()
    return MockProvider(model=os.getenv("LLM_MODEL", "mock-model-1"))
