"""
api_or_scraper.py
=================
Funciones de conexion externa para datos live de criptomonedas.

Actualmente usa la API publica de CoinGecko para precios actuales y series
recientes. Se mantiene separado de processing.py para que el procesamiento
historico y la capa de datos externos no queden mezclados.
"""

import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


COINGECKO_IDS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Litecoin": "litecoin",
    "Dash": "dash",
    "Monero": "monero",
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
