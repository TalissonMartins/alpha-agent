import sqlite3
from pathlib import Path

import pandas as pd


def gravar_rodada(path: Path, alocacao: pd.DataFrame, mudancas: pd.DataFrame) -> int:
    path.parent.mkdir(exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS rodadas (id INTEGER PRIMARY KEY, total_brl REAL, mudancas INTEGER)"
        )
        total = float(alocacao["valor_brl"].sum()) if not alocacao.empty else 0.0
        cur = conn.execute(
            "INSERT INTO rodadas (total_brl, mudancas) VALUES (?, ?)",
            (round(total, 2), int(len(mudancas))),
        )
        conn.commit()
        return int(cur.lastrowid)


def ultimas(path: Path, limite: int = 5) -> list[dict]:
    if not path.exists():
        return []
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        linhas = conn.execute(
            "SELECT id, total_brl, mudancas FROM rodadas ORDER BY id DESC LIMIT ?",
            (limite,),
        ).fetchall()
    return [dict(linha) for linha in linhas]
