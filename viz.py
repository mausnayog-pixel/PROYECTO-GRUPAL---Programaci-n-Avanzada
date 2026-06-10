"""
viz.py
======
Funciones de visualización para el dashboard de criptomonedas.
Todas retornan objetos plotly.graph_objects.Figure.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Paleta de colores por moneda ──────────────────────────────────────────────
COLORES_MONEDA = {
    "Bitcoin":  "#F7931A",
    "Ethereum": "#627EEA",
    "Litecoin": "#BFBBBB",
    "Dash":     "#008CE7",
    "Monero":   "#FF6600",
}

COLOR_FONDO   = "#0F0F1A"
COLOR_PANEL   = "#1A1A2E"
COLOR_ACENTO  = "#E94560"
COLOR_TEXTO   = "#E0E0E0"
COLOR_GRID    = "#2A2A3E"

LAYOUT_BASE = dict(
    font=dict(family="IBM Plex Sans, sans-serif", color=COLOR_TEXTO, size=12),
    plot_bgcolor=COLOR_PANEL,
    paper_bgcolor=COLOR_PANEL,
    margin=dict(l=20, r=20, t=45, b=30),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=COLOR_GRID,
        borderwidth=1,
        font_size=11,
    ),
    xaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
    yaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
)


def _color(moneda: str) -> str:
    return COLORES_MONEDA.get(moneda, COLOR_ACENTO)


# ══════════════════════════════════════════════════════════════════════════════
# 1. PRECIO EN EL TIEMPO (línea)
# ══════════════════════════════════════════════════════════════════════════════

def grafico_precio_tiempo(df: pd.DataFrame,
                          monedas: list[str],
                          escala_log: bool = False) -> go.Figure:
    """
    Gráfico de líneas: evolución del precio de cierre por moneda.

    Parámetros
    ----------
    df        : DataFrame limpio
    monedas   : lista de monedas a graficar
    escala_log: si True usa escala logarítmica en Y
    """
    df_fil = df[df["name"].isin(monedas)].copy()

    fig = go.Figure()
    for moneda in monedas:
        sub = df_fil[df_fil["name"] == moneda].sort_values("date")
        fig.add_trace(go.Scatter(
            x=sub["date"],
            y=sub["close"],
            name=moneda,
            mode="lines",
            line=dict(color=_color(moneda), width=2),
            hovertemplate=(
                f"<b>{moneda}</b><br>"
                "Fecha: %{x|%d %b %Y}<br>"
                "Precio: $%{y:,.2f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Evolución del Precio de Cierre (USD)", font_size=14),
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)" + (" — escala log" if escala_log else ""),
        yaxis_type="log" if escala_log else "linear",
        height=420,
        hovermode="x unified",
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 2. VELA JAPONESA (candlestick) — una moneda a la vez
# ══════════════════════════════════════════════════════════════════════════════

def grafico_velas(df: pd.DataFrame, moneda: str) -> go.Figure:
    """
    Gráfico de velas japonesas (open/high/low/close) para una moneda.

    Parámetros
    ----------
    df     : DataFrame limpio
    moneda : nombre de la moneda a graficar
    """
    sub = df[df["name"] == moneda].sort_values("date")

    fig = go.Figure(go.Candlestick(
        x=sub["date"],
        open=sub["open"],
        high=sub["high"],
        low=sub["low"],
        close=sub["close"],
        increasing_line_color="#26A69A",
        decreasing_line_color=COLOR_ACENTO,
        name=moneda,
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Velas Japonesas — {moneda}", font_size=14),
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)",
        xaxis_rangeslider_visible=False,
        height=420,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 3. VOLUMEN DE TRANSACCIONES (barras)
# ══════════════════════════════════════════════════════════════════════════════

def grafico_volumen(df: pd.DataFrame, moneda: str) -> go.Figure:
    """
    Gráfico de barras: volumen diario de transacciones para una moneda.

    Parámetros
    ----------
    df     : DataFrame limpio
    moneda : nombre de la moneda
    """
    sub = df[df["name"] == moneda].sort_values("date")

    fig = go.Figure(go.Bar(
        x=sub["date"],
        y=sub["volume"],
        marker_color=_color(moneda),
        opacity=0.75,
        name="Volumen",
        hovertemplate="Fecha: %{x|%d %b %Y}<br>Volumen: $%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Volumen Diario — {moneda}", font_size=14),
        xaxis_title="Fecha",
        yaxis_title="Volumen (USD)",
        height=300,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 4. VOLATILIDAD COMPARATIVA (barras horizontales)
# ══════════════════════════════════════════════════════════════════════════════

def grafico_volatilidad(metricas: pd.DataFrame) -> go.Figure:
    """
    Barras horizontales comparando la volatilidad anual de cada moneda.

    Parámetros
    ----------
    metricas : DataFrame resultado de calcular_metricas()
    """
    df_vol = (
        metricas[["Volatilidad Anual (%)"]]
        .reset_index()
        .sort_values("Volatilidad Anual (%)", ascending=True)
    )

    colores = [_color(m) for m in df_vol["Moneda"]]

    fig = go.Figure(go.Bar(
        x=df_vol["Volatilidad Anual (%)"],
        y=df_vol["Moneda"],
        orientation="h",
        marker_color=colores,
        text=df_vol["Volatilidad Anual (%)"].round(1).astype(str) + "%",
        textposition="outside",
        textfont=dict(color=COLOR_TEXTO, size=11),
        hovertemplate="<b>%{y}</b><br>Volatilidad anual: %{x:.2f}%<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Volatilidad Anual por Moneda", font_size=14),
        xaxis_title="Volatilidad Anual (%)",
        xaxis_ticksuffix="%",
        yaxis_title="",
        height=320,
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 5. HISTOGRAMA DE RETORNOS DIARIOS
# ══════════════════════════════════════════════════════════════════════════════

def grafico_histograma_retornos(df: pd.DataFrame, moneda: str) -> go.Figure:
    """
    Histograma de retornos diarios porcentuales para una moneda.

    Parámetros
    ----------
    df     : DataFrame limpio
    moneda : nombre de la moneda
    """
    sub = df[df["name"] == moneda].sort_values("date")
    retornos = sub["close"].pct_change().dropna() * 100

    fig = go.Figure(go.Histogram(
        x=retornos,
        nbinsx=60,
        marker_color=_color(moneda),
        opacity=0.8,
        name=moneda,
        hovertemplate="Retorno: %{x:.2f}%<br>Frecuencia: %{y}<extra></extra>",
    ))

    media = retornos.mean()
    fig.add_vline(
        x=media,
        line_dash="dash",
        line_color=COLOR_ACENTO,
        annotation_text=f"Media: {media:.2f}%",
        annotation_font_color=COLOR_ACENTO,
        annotation_position="top right",
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"Distribución de Retornos Diarios — {moneda}", font_size=14),
        xaxis_title="Retorno diario (%)",
        xaxis_ticksuffix="%",
        yaxis_title="Frecuencia",
        height=320,
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 6. PIE CHART — PESOS DEL PORTAFOLIO ÓPTIMO
# ══════════════════════════════════════════════════════════════════════════════

def grafico_pesos_portafolio(pesos: dict) -> go.Figure:
    """
    Gráfico de pie con los pesos del portafolio de mínima varianza.

    Parámetros
    ----------
    pesos : dict {moneda: peso} resultado de optimizar_portafolio()
    """
    monedas = list(pesos.keys())
    valores = [p * 100 for p in pesos.values()]
    colores = [_color(m) for m in monedas]

    fig = go.Figure(go.Pie(
        labels=monedas,
        values=valores,
        marker=dict(colors=colores, line=dict(color=COLOR_FONDO, width=2)),
        textinfo="label+percent",
        textfont_size=12,
        hole=0.4,
        hovertemplate="<b>%{label}</b><br>Peso: %{value:.2f}%<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Portafolio de Mínima Varianza — Pesos Óptimos", font_size=14),
        height=380,
        showlegend=True,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 7. FRONTERA EFICIENTE
# ══════════════════════════════════════════════════════════════════════════════

def grafico_frontera_eficiente(frontera: list[dict],
                                vol_opt: float,
                                ret_opt: float) -> go.Figure:
    """
    Curva de la frontera eficiente con el punto de mínima varianza marcado.

    Parámetros
    ----------
    frontera : lista de dicts {volatilidad, retorno} de optimizar_portafolio()
    vol_opt  : volatilidad del portafolio óptimo (%)
    ret_opt  : retorno esperado del portafolio óptimo (%)
    """
    vols = [p["volatilidad"] for p in frontera]
    rets = [p["retorno"]     for p in frontera]

    fig = go.Figure()

    # Curva frontera
    fig.add_trace(go.Scatter(
        x=vols,
        y=rets,
        mode="lines",
        line=dict(color="#627EEA", width=2.5),
        name="Frontera Eficiente",
        hovertemplate="Volatilidad: %{x:.2f}%<br>Retorno: %{y:.2f}%<extra></extra>",
    ))

    # Punto óptimo
    fig.add_trace(go.Scatter(
        x=[vol_opt],
        y=[ret_opt],
        mode="markers",
        marker=dict(color=COLOR_ACENTO, size=14, symbol="star",
                    line=dict(color="white", width=1.5)),
        name="Mínima Varianza",
        hovertemplate=(
            f"<b>Portafolio Óptimo</b><br>"
            f"Volatilidad: {vol_opt:.2f}%<br>"
            f"Retorno: {ret_opt:.2f}%<extra></extra>"
        ),
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="Frontera Eficiente (Markowitz)", font_size=14),
        xaxis_title="Volatilidad Anual (%)",
        yaxis_title="Retorno Esperado Anual (%)",
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        height=400,
    )
    return fig