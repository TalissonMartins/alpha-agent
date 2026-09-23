import logging
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger("AlphaAgent-Engine")

# Premissas institucionais (podem ser parametrizadas depois)
TAXA_DESCONTO_K = 0.12          # 12% a.a. (custo de capital / retorno exigido)
CRESCIMENTO_G = 0.04            # 4% a.a. (crescimento perpétuo conservador)


def _safe_div(a, b) -> Optional[float]:
    """Divisão segura."""
    try:
        if a is None or b is None or b == 0:
            return None
        return float(a) / float(b)
    except (TypeError, ValueError):
        return None


def _calc_graham(preco, pl, pvp) -> Optional[float]:
    """Graham Number clássico."""
    eps = _safe_div(preco, pl)
    bvps = _safe_div(preco, pvp)

    if eps is None or bvps is None or eps <= 0 or bvps <= 0:
        return None

    try:
        return round(float(np.sqrt(22.5 * eps * bvps)), 2)
    except (ValueError, TypeError):
        return None


def _calc_margem_seguranca(preco, valor_justo) -> Optional[float]:
    """Margem de Segurança (%) em relação a qualquer preço justo."""
    if valor_justo is None or valor_justo <= 0 or preco is None or preco <= 0:
        return None
    try:
        return round(((valor_justo - preco) / valor_justo) * 100, 2)
    except (TypeError, ValueError):
        return None


def _calc_gordon(preco, dy_percent) -> Optional[float]:
    """
    Modelo de Gordon Growth (versão simplificada institucional).
    D0 = Preço * (DY/100)
    D1 = D0 * (1 + g)
    P0 = D1 / (k - g)
    """
    if preco is None or dy_percent is None or preco <= 0:
        return None

    try:
        d0 = preco * (float(dy_percent) / 100)
        if d0 <= 0:
            return None

        d1 = d0 * (1 + CRESCIMENTO_G)

        if TAXA_DESCONTO_K <= CRESCIMENTO_G:
            return None  # evita divisão por zero ou negativa

        gordon = d1 / (TAXA_DESCONTO_K - CRESCIMENTO_G)
        return round(float(gordon), 2)
    except (TypeError, ValueError):
        return None


def _calc_earnings_yield(pl) -> Optional[float]:
    """Earnings Yield = 1 / P/L (em %)."""
    if pl is None or pl <= 0:
        return None
    try:
        return round((1 / float(pl)) * 100, 2)
    except (TypeError, ValueError):
        return None


def calculate_valuation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece o DataFrame com indicadores de valuation da Fase 2.
    """
    if df.empty:
        logger.warning("DataFrame vazio recebido pelo motor financeiro.")
        return df.copy()

    df_enriquecido = df.copy()

    graham_list = []
    margem_graham_list = []
    gordon_list = []
    margem_gordon_list = []
    earnings_yield_list = []

    for _, row in df_enriquecido.iterrows():
        preco = row.get("Preco_Atual")
        pl = row.get("PL")
        pvp = row.get("PVP")
        dy = row.get("Dividend_Yield_%")

        # Graham
        graham = _calc_graham(preco, pl, pvp)
        margem_graham = _calc_margem_seguranca(preco, graham)

        # Gordon
        gordon = _calc_gordon(preco, dy)
        margem_gordon = _calc_margem_seguranca(preco, gordon)

        # Earnings Yield
        ey = _calc_earnings_yield(pl)

        graham_list.append(graham)
        margem_graham_list.append(margem_graham)
        gordon_list.append(gordon)
        margem_gordon_list.append(margem_gordon)
        earnings_yield_list.append(ey)

    df_enriquecido["Preco_Justo_Graham"] = graham_list
    df_enriquecido["Margem_Graham_%"] = margem_graham_list
    df_enriquecido["Preco_Justo_Gordon"] = gordon_list
    df_enriquecido["Margem_Gordon_%"] = margem_gordon_list
    df_enriquecido["Earnings_Yield_%"] = earnings_yield_list

    logger.info("Motor financeiro (Graham + Gordon + Earnings Yield) executado com sucesso.")
    return df_enriquecido