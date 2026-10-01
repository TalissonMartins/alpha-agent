from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("AlphaAgent-Engine")

_K = 0.12
_G = 0.04
_REQUIRED = ("Preco_Atual", "PL", "PVP", "Dividend_Yield_%")


def _num(value: object) -> Optional[float]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_valuation(df: pd.DataFrame) -> pd.DataFrame:
    missing = [col for col in _REQUIRED if col not in df.columns]
    if missing:
        raise ValueError(f"Coluna obrigatoria ausente: {missing[0]}")

    out = df.copy()
    grahams: list[Optional[float]] = []
    margins: list[Optional[float]] = []
    yields: list[Optional[float]] = []
    gordons: list[Optional[float]] = []

    for _, row in out.iterrows():
        price = _num(row.get("Preco_Atual"))
        pl = _num(row.get("PL"))
        pvp = _num(row.get("PVP"))
        dy = _num(row.get("Dividend_Yield_%"))

        lpa = price / pl if price and pl and pl > 0 else None
        vpa = price / pvp if price and pvp and pvp > 0 else None
        if lpa and vpa and lpa > 0 and vpa > 0:
            graham = round(float(np.sqrt(22.5 * lpa * vpa)), 2)
        else:
            graham = None
        grahams.append(graham)

        if graham and price and graham > 0 and price > 0:
            margins.append(round(((graham - price) / graham) * 100, 2))
        else:
            margins.append(None)

        yields.append(round(100 / pl, 2) if pl and pl > 0 else None)

        if price and dy is not None and price > 0 and (_K - _G) > 0:
            dividendo = price * (dy / 100)
            gordon = round(dividendo * (1 + _G) / (_K - _G), 2)
        else:
            gordon = None
        gordons.append(gordon)

    out["Preco_Justo_Graham"] = grahams
    out["Margem_Graham_%"] = margins
    out["Earnings_Yield_%"] = yields
    out["Preco_Justo_Gordon"] = gordons
    logger.info("Valuation calculado para %d linhas.", len(out))
    return out
