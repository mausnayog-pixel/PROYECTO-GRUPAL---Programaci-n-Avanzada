"""
processing.py
=============
Carga, limpieza, métricas descriptivas y optimización de portafolio
para el dashboard de criptomonedas (crypto-markets.csv).

Fuente del dataset : CoinMarketCap Historical Data via Kaggle
URL                : https://www.kaggle.com/datasets/jessevent/all-crypto-currencies
Licencia           : CC0 — Public Domain
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize

# ── Constantes ────────────────────────────────────────────────────────────────
TOP5_DEFAULT = ["Bitcoin", "Ethereum", "Litecoin", "Dash", "Monero"]
COLUMNAS_REQUERIDAS = {"name", "date", "open", "high", "low", "close", "volume", "market"}


# ══════════════════════════════════════════════════════════════════════════════
# 1. CARGA
# ══════════════════════════════════════════════════════════════════════════════

def cargar_datos(ruta: str) -> pd.DataFrame:
    """
    Carga el archivo CSV de mercados de criptomonedas.

    Parámetros
    ----------
    ruta : str  — ruta relativa o absoluta al .csv

    Retorna
    -------
    pd.DataFrame con los datos crudos.

    Lanza
    -----
    FileNotFoundError si la ruta no existe.
    ValueError si faltan columnas requeridas.
    """
    df = pd.read_csv(ruta, encoding="utf-8")

    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(f"El CSV no contiene las columnas requeridas: {faltantes}")

    return df


# ══════════════════════════════════════════════════════════════════════════════
# 2. LIMPIEZA
# ══════════════════════════════════════════════════════════════════════════════

def limpiar_datos(df: pd.DataFrame,
                  monedas: list[str] | None = None) -> pd.DataFrame:
    """
    Aplica limpieza completa al DataFrame:
      - Filtra las monedas de interés
      - Convierte tipos de datos
      - Elimina duplicados y nulos en columnas clave
      - Descarta filas con precios <= 0 o volumen nulo
      - Ordena por moneda y fecha

    Parámetros
    ----------
    df     : DataFrame crudo (resultado de cargar_datos)
    monedas: lista de nombres de monedas a conservar;
             None = usa TOP5_DEFAULT

    Retorna
    -------
    pd.DataFrame limpio y ordenado.
    """
    if monedas is None:
        monedas = TOP5_DEFAULT

    # 1. Filtrar monedas de interés
    df = df[df["name"].isin(monedas)].copy()

    # 2. Convertir fecha
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 3. Convertir columnas numéricas
    numericas = ["open", "high", "low", "close", "volume", "market",
                 "close_ratio", "spread"]
    for col in numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Eliminar duplicados exactos
    df = df.drop_duplicates()

    # 5. Eliminar filas con nulos en columnas clave
    df = df.dropna(subset=["date", "close", "volume", "market"])

    # 6. Descartar precios y volumen no positivos
    df = df[df["close"] > 0]
    df = df[df["volume"] > 0]

    # 7. Ordenar
    df = df.sort_values(["name", "date"]).reset_index(drop=True)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# 3. MÉTRICAS DESCRIPTIVAS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas descriptivas por moneda:
      precio_medio, precio_max, precio_min, volumen_medio,
      market_cap_max, retorno_total, volatilidad_anual, n_registros.

    Parámetros
    ----------
    df : DataFrame limpio

    Retorna
    -------
    pd.DataFrame con una fila por moneda.
    """
    registros = []

    for moneda, grupo in df.groupby("name"):
        grupo = grupo.sort_values("date")
        retornos = grupo["close"].pct_change().dropna()

        precio_inicio = grupo["close"].iloc[0]
        precio_fin    = grupo["close"].iloc[-1]
        retorno_total = ((precio_fin - precio_inicio) / precio_inicio) * 100

        registros.append({
            "Moneda":              moneda,
            "Precio Medio (USD)":  round(grupo["close"].mean(), 4),
            "Precio Máx (USD)":    round(grupo["close"].max(), 4),
            "Precio Mín (USD)":    round(grupo["close"].min(), 4),
            "Volumen Medio (USD)": round(grupo["volume"].mean(), 0),
            "Market Cap Máx":      round(grupo["market"].max(), 0),
            "Retorno Total (%)":   round(retorno_total, 2),
            "Volatilidad Anual (%)": round(retornos.std() * np.sqrt(365) * 100, 2),
            "Registros":           len(grupo),
            "Desde":               grupo["date"].min().strftime("%Y-%m-%d"),
            "Hasta":               grupo["date"].max().strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(registros).set_index("Moneda")


# ══════════════════════════════════════════════════════════════════════════════
# 4. RETORNOS DIARIOS
# ══════════════════════════════════════════════════════════════════════════════

def calcular_retornos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye una tabla pivote de retornos diarios logarítmicos
    por moneda (columnas = monedas, índice = fecha).

    Parámetros
    ----------
    df : DataFrame limpio

    Retorna
    -------
    pd.DataFrame de retornos log diarios, sin NaN.
    """
    pivot = (
        df.pivot_table(index="date", columns="name", values="close")
          .sort_index()
    )
    # Retornos logarítmicos: más estables para la optimización
    retornos = np.log(pivot / pivot.shift(1)).dropna()
    return retornos


# ══════════════════════════════════════════════════════════════════════════════
# 5. OPTIMIZACIÓN DE PORTAFOLIO — MÍNIMA VARIANZA (MARKOWITZ)
# ══════════════════════════════════════════════════════════════════════════════

def _volatilidad_portafolio(pesos: np.ndarray,
                             cov_anual: np.ndarray) -> float:
    """Función objetivo: volatilidad anualizada del portafolio."""
    return float(np.sqrt(pesos @ cov_anual @ pesos))


def optimizar_portafolio(retornos: pd.DataFrame) -> dict:
    """
    Calcula el portafolio de mínima varianza usando scipy.optimize.minimize
    con restricciones: suma de pesos = 1, pesos en [0, 1] (sin posiciones cortas).

    Parámetros
    ----------
    retornos : DataFrame de retornos log diarios (resultado de calcular_retornos)

    Retorna
    -------
    dict con claves:
        pesos        — dict {moneda: peso_optimo}
        volatilidad  — volatilidad anual del portafolio óptimo (%)
        retorno      — retorno anual esperado del portafolio (%)
        sharpe       — Sharpe ratio (tasa libre de riesgo = 0)
        frontera     — lista de puntos (volatilidad, retorno) de la frontera eficiente
    """
    n = len(retornos.columns)
    monedas = list(retornos.columns)

    # Matriz de covarianza anualizada (365 días)
    cov_anual  = retornos.cov().values * 365
    ret_anual  = retornos.mean().values * 365   # retornos anuales esperados

    # Restricciones y límites
    restricciones = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    limites = tuple((0.0, 1.0) for _ in range(n))
    w0 = np.ones(n) / n   # punto de inicio: pesos iguales

    resultado = minimize(
        _volatilidad_portafolio,
        w0,
        args=(cov_anual,),
        method="SLSQP",
        bounds=limites,
        constraints=restricciones,
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    pesos_opt = resultado.x
    vol_opt   = _volatilidad_portafolio(pesos_opt, cov_anual) * 100
    ret_opt   = float(pesos_opt @ ret_anual) * 100
    sharpe    = ret_opt / vol_opt if vol_opt > 0 else 0.0

    # ── Frontera eficiente ────────────────────────────────────────────────────
    # Barremos retornos objetivo entre el mínimo y el máximo posible
    ret_min = float(ret_anual.min()) * 100
    ret_max = float(ret_anual.max()) * 100
    puntos_frontera = []

    for ret_objetivo in np.linspace(ret_min, ret_max, 60):
        rest_frontera = restricciones + [{
            "type": "eq",
            "fun": lambda w, r=ret_objetivo/100: float(w @ ret_anual) - r,
        }]
        res = minimize(
            _volatilidad_portafolio,
            w0,
            args=(cov_anual,),
            method="SLSQP",
            bounds=limites,
            constraints=rest_frontera,
            options={"ftol": 1e-10, "maxiter": 500},
        )
        if res.success:
            puntos_frontera.append({
                "volatilidad": round(_volatilidad_portafolio(res.x, cov_anual) * 100, 4),
                "retorno":     round(float(res.x @ ret_anual) * 100, 4),
            })

    return {
        "pesos":       {m: round(float(p), 6) for m, p in zip(monedas, pesos_opt)},
        "volatilidad": round(vol_opt, 4),
        "retorno":     round(ret_opt, 4),
        "sharpe":      round(sharpe, 4),
        "frontera":    puntos_frontera,
    }
