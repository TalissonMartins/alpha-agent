import pandas as pd


def classificar_fii(df: pd.DataFrame) -> pd.DataFrame:
    """P/VP abaixo de 1 e desconto patrimonial. Nao e ordem."""
    out = df.copy()
    status = []
    for valor in out.get("PVP", []):
        if valor is None or valor != valor or float(valor) <= 0:
            status.append("INCOMPLETO")
        elif float(valor) < 1:
            status.append("DESCONTO")
        elif float(valor) == 1:
            status.append("NO_VP")
        else:
            status.append("PREMIO")
    out["Status_FII"] = status
    return out
