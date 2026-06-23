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
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time

# ── Constantes ────────────────────────────────────────────────────────────────
TOP5_DEFAULT = ["Bitcoin", "Ethereum", "Litecoin", "Dash", "Monero"]
COLUMNAS_REQUERIDAS = {"name", "date", "open", "high", "low", "close", "volume", "market"}
COINGECKO_IDS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Litecoin": "litecoin",
    "Dash": "dash",
    "Monero": "monero",
}


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


def optimizar_portafolio(
    retornos: pd.DataFrame,
    tasa_libre_riesgo: float = 0.0,
    perfil_riesgo: str = "Conservador",
) -> dict:
    """
    Calcula un portafolio óptimo usando scipy.optimize.minimize
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
        sharpe       — Sharpe ratio con tasa libre de riesgo anual
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

    def _retorno_portafolio(pesos: np.ndarray) -> float:
        return float(pesos @ ret_anual)

    def _sharpe_negativo(pesos: np.ndarray) -> float:
        vol = _volatilidad_portafolio(pesos, cov_anual) * 100
        ret = _retorno_portafolio(pesos) * 100
        return -((ret - tasa_libre_riesgo) / vol) if vol > 0 else 0.0

    perfil = perfil_riesgo.lower()
    if perfil == "balanceado":
        objetivo = _sharpe_negativo
        args_objetivo = ()
    elif perfil == "agresivo":
        objetivo = lambda w: -_retorno_portafolio(w)
        args_objetivo = ()
    else:
        objetivo = _volatilidad_portafolio
        args_objetivo = (cov_anual,)

    resultado = minimize(
        objetivo,
        w0,
        args=args_objetivo,
        method="SLSQP",
        bounds=limites,
        constraints=restricciones,
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    pesos_opt = resultado.x
    vol_opt   = _volatilidad_portafolio(pesos_opt, cov_anual) * 100
    ret_opt   = float(pesos_opt @ ret_anual) * 100
    sharpe    = (ret_opt - tasa_libre_riesgo) / vol_opt if vol_opt > 0 else 0.0

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
        "perfil":      perfil_riesgo,
    }


def _coingecko_get(path: str, params: dict) -> dict | list:
    """Consulta simple a la API publica de CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/{path}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "accept": "application/json",
            "user-agent": "crypto-portfolio-dashboard/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def obtener_precios_coingecko(monedas: list[str]) -> pd.DataFrame:
    """
    Obtiene precio, variacion 24h, volumen y market cap actual desde CoinGecko.
    """
    ids = [COINGECKO_IDS[m] for m in monedas if m in COINGECKO_IDS]
    if not ids:
        return pd.DataFrame()

    data = _coingecko_get(
        "simple/price",
        {
            "ids": ",".join(ids),
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
            "include_last_updated_at": "true",
        },
    )

    id_to_name = {v: k for k, v in COINGECKO_IDS.items()}
    rows = []
    for coin_id, values in data.items():
        rows.append({
            "name": id_to_name.get(coin_id, coin_id.title()),
            "price": values.get("usd"),
            "market_cap": values.get("usd_market_cap"),
            "volume_24h": values.get("usd_24h_vol"),
            "change_24h": values.get("usd_24h_change"),
            "last_updated": pd.to_datetime(values.get("last_updated_at"), unit="s", utc=True),
        })
    return pd.DataFrame(rows)


def obtener_market_chart_coingecko(monedas: list[str], dias: int = 30) -> pd.DataFrame:
    """
    Descarga precios historicos recientes de CoinGecko para modo live.
    """
    frames = []
    for moneda in monedas:
        coin_id = COINGECKO_IDS.get(moneda)
        if not coin_id:
            continue
        if frames:
            time.sleep(1.1)
        data = _coingecko_get(
            f"coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": dias, "interval": "daily"},
        )
        market_caps = dict(data.get("market_caps", []))
        volumes = dict(data.get("total_volumes", []))
        rows = []
        for ts, price in data.get("prices", []):
            rows.append({
                "name": moneda,
                "date": pd.to_datetime(ts, unit="ms", utc=True).tz_convert(None),
                "close": price,
                "open": price,
                "high": price,
                "low": price,
                "volume": volumes.get(ts, np.nan),
                "market": market_caps.get(ts, np.nan),
            })
        frames.append(pd.DataFrame(rows))

    if not frames:
        return pd.DataFrame(columns=["name", "date", "open", "high", "low", "close", "volume", "market"])
    return pd.concat(frames, ignore_index=True).dropna(subset=["date", "close"])


def calcular_backtest_portafolio(df: pd.DataFrame, pesos: dict, inversion_inicial: float = 1000.0) -> pd.DataFrame:
    """
    Simula el valor acumulado de un portafolio buy-and-hold con pesos dados.
    """
    precios = df.pivot_table(index="date", columns="name", values="close").sort_index()
    monedas = [m for m in pesos if m in precios.columns]
    precios = precios[monedas].dropna()
    if precios.empty:
        return pd.DataFrame()

    normalizado = precios / precios.iloc[0]
    ponderaciones = pd.Series({m: pesos[m] for m in monedas})
    valor_portafolio = normalizado.mul(ponderaciones, axis=1).sum(axis=1) * inversion_inicial
    resultado = normalizado * inversion_inicial
    resultado["Portafolio optimo"] = valor_portafolio
    return resultado.reset_index().melt(id_vars="date", var_name="Serie", value_name="Valor")
