"""Agente de brinquedo com ferramentas, para a licao 5.

Nao tem nada de inteligente aqui - a escolha de ferramenta e' aleatoria de
proposito. O que interessa e' a FORMA: um agente e' um laco que chama o
modelo, executa ferramenta, volta pro modelo, e para em algum momento. As
metricas que importam sao sobre esse laco, nao sobre a resposta.
"""
from __future__ import annotations

import random
import time

import metrics as m
from provider import ProviderError

MAX_STEPS = 8


def _tool_busca(_: str) -> str:
    time.sleep(random.uniform(0.02, 0.3))
    return "3 resultados"


def _tool_calculadora(_: str) -> str:
    time.sleep(random.uniform(0.005, 0.05))
    return "42"


def _tool_banco(_: str) -> str:
    time.sleep(random.uniform(0.05, 1.5))
    if random.random() < 0.08:
        raise RuntimeError("conexao recusada")
    return "12 linhas"


TOOLS = {"busca": _tool_busca, "calculadora": _tool_calculadora, "banco": _tool_banco}


def run_agent(provider, task: str, agent_name: str = "agente-demo") -> dict:
    started = time.perf_counter()
    inference_calls = 0
    tool_calls = 0
    outcome = "ok"

    try:
        for step in range(MAX_STEPS):
            # 1. chama o modelo
            inference_calls += 1
            try:
                provider.complete(f"[passo {step}] {task}")
            except ProviderError as e:
                m.errors_total.labels(provider.name, provider.model, e.error_type).inc()
                outcome = "error"
                break

            # 2. o modelo "decide" se quer ferramenta
            if random.random() < 0.45:
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
            # Esgotou os passos sem concluir. Este contador e' um dos sinais
            # mais uteis de um agente: se ele sobe, o agente esta' rodando em
            # circulo, gastando token e nao entregando resposta.
            outcome = "steps_exhausted"
            m.agent_steps_exhausted.labels(agent_name).inc()
    finally:
        m.agent_duration.labels(agent_name, outcome).observe(time.perf_counter() - started)
        m.agent_inference_calls.labels(agent_name).observe(inference_calls)
        m.agent_tool_calls.labels(agent_name).observe(tool_calls)

    return {
        "outcome": outcome,
        "inference_calls": inference_calls,
        "tool_calls": tool_calls,
    }
