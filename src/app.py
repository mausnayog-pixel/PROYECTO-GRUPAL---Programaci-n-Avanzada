"""
app.py
======
Dashboard principal del análisis de portafolio de criptomonedas.
Fuente de datos: CoinMarketCap Historical Data (Kaggle, CC0)
URL: https://www.kaggle.com/datasets/jessevent/all-crypto-currencies
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from processing import (
    cargar_datos,
    limpiar_datos,
    calcular_metricas,
    calcular_retornos,
    optimizar_portafolio,
    TOP5_DEFAULT,
)
from viz import (
    grafico_precio_tiempo,
    grafico_velas,
    grafico_volumen,
    grafico_volatilidad,
    grafico_histograma_retornos,
    grafico_pesos_portafolio,
    grafico_frontera_eficiente,
)

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Portfolio Dashboard",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.header-box {
    background: #1A1A2E;
    border-left: 5px solid #E94560;
    border-radius: 10px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.5rem;
}
.header-box h1 {
    font-family: 'IBM Plex Mono', monospace;
    color: #F7F5F0;
    font-size: 1.6rem;
    margin: 0 0 0.3rem 0;
}
.header-box p { color: #A0A0B0; margin: 0; font-size: 0.85rem; }

.kpi-card {
    background: #1A1A2E;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    text-align: center;
    border-top: 3px solid #E94560;
}
.kpi-card .kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #A0A0B0;
    margin-bottom: 0.4rem;
}
.kpi-card .kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #E94560;
}
.kpi-card .kpi-sub {
    font-size: 0.7rem;
    color: #A0A0B0;
    margin-top: 0.2rem;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #E94560;
    border-bottom: 1px solid #E94560;
    padding-bottom: 0.3rem;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🪙 Crypto Portfolio Dashboard</h1>
    <p>Análisis de precios históricos y optimización de portafolio de mínima varianza (Markowitz) · 2013–2018</p>
</div>
""", unsafe_allow_html=True)

# ── Carga de datos (cacheada) ─────────────────────────────────────────────────
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "crypto-markets.csv")

@st.cache_data(show_spinner="Cargando datos...")
def obtener_datos(monedas: tuple) -> pd.DataFrame:
    df_raw = cargar_datos(RUTA_CSV)
    return limpiar_datos(df_raw, monedas=list(monedas))

@st.cache_data(show_spinner="Optimizando portafolio...")
def obtener_portafolio(monedas: tuple):
    df = obtener_datos(monedas)
    retornos = calcular_retornos(df)
    return optimizar_portafolio(retornos)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Controles")
    st.markdown("---")

    # Control 1: selección de monedas
    monedas_sel = st.multiselect(
        "Criptomonedas",
        options=TOP5_DEFAULT,
        default=TOP5_DEFAULT,
        help="Elige las monedas para analizar y construir el portafolio.",
    )

    if not monedas_sel:
        st.warning("Selecciona al menos una moneda.")
        st.stop()

    st.markdown("---")

    # Control 2: rango de fechas
    df_all = obtener_datos(tuple(TOP5_DEFAULT))
    fecha_min = df_all["date"].min().date()
    fecha_max = df_all["date"].max().date()

    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        help="Filtra el período de análisis.",
    )

    if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
        fecha_inicio, fecha_fin = rango_fechas
    else:
        fecha_inicio, fecha_fin = fecha_min, fecha_max

    st.markdown("---")

    # Control 3: escala logarítmica
    escala_log = st.toggle(
        "Escala logarítmica",
        value=False,
        help="Útil para comparar monedas con precios muy diferentes.",
    )

    # Control 4: moneda individual para análisis
    moneda_individual = st.selectbox(
        "Moneda para análisis individual",
        options=monedas_sel,
        help="Moneda que se usará en velas, volumen e histograma.",
    )

    st.markdown("---")
    st.caption("Fuente: CoinMarketCap via Kaggle (CC0)")
    st.caption("Programación Avanzada · 2025")

# ── Filtrado por fechas ───────────────────────────────────────────────────────
df = obtener_datos(tuple(monedas_sel))
df = df[
    (df["date"].dt.date >= fecha_inicio) &
    (df["date"].dt.date <= fecha_fin)
]

if df.empty:
    st.error("No hay datos para el rango de fechas seleccionado.")
    st.stop()

# ── Métricas y portafolio ─────────────────────────────────────────────────────
metricas = calcular_metricas(df)

# Portafolio solo si hay ≥2 monedas
hay_portafolio = len(monedas_sel) >= 2
if hay_portafolio:
    portafolio = obtener_portafolio(tuple(monedas_sel))

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📈  Precios & Mercado",
    "🏦  Portafolio Óptimo",
    "📋  Datos",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Precios & Mercado
# ─────────────────────────────────────────────────────────────────────────────
with tab1:

    # KPIs
    st.markdown('<p class="section-label">Indicadores clave del período</p>',
                unsafe_allow_html=True)

    def fmt_usd(v):
        if v >= 1_000:
            return f"${v:,.0f}"
        elif v >= 1:
            return f"${v:,.2f}"
        else:
            return f"${v:.4f}"

    def kpi(col, label, value, sub=""):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    cols = st.columns(len(monedas_sel))
    for i, moneda in enumerate(monedas_sel):
        if moneda in metricas.index:
            row = metricas.loc[moneda]
            kpi(
                cols[i],
                moneda,
                fmt_usd(row["Precio Medio (USD)"]),
                f"Ret: {row['Retorno Total (%)']:+.0f}%  |  Vol: {row['Volatilidad Anual (%)']:.0f}%",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de precios
    st.markdown('<p class="section-label">Evolución de precios</p>',
                unsafe_allow_html=True)
    st.plotly_chart(
        grafico_precio_tiempo(df, monedas_sel, escala_log),
        use_container_width=True,
    )

    # Velas + Volumen
    col_velas, col_vol = st.columns([3, 2])
    with col_velas:
        st.markdown('<p class="section-label">Velas japonesas</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            grafico_velas(df, moneda_individual),
            use_container_width=True,
        )
    with col_vol:
        st.markdown('<p class="section-label">Volumen diario</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            grafico_volumen(df, moneda_individual),
            use_container_width=True,
        )

    # Volatilidad + Histograma
    col_vol2, col_hist = st.columns(2)
    with col_vol2:
        st.markdown('<p class="section-label">Volatilidad anual comparativa</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            grafico_volatilidad(metricas),
            use_container_width=True,
        )
    with col_hist:
        st.markdown('<p class="section-label">Distribución de retornos diarios</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(
            grafico_histograma_retornos(df, moneda_individual),
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Portafolio Óptimo
# ─────────────────────────────────────────────────────────────────────────────
with tab2:

    if not hay_portafolio:
        st.info("Selecciona al menos 2 monedas en el panel lateral para calcular el portafolio óptimo.")
    else:
        # KPIs del portafolio
        st.markdown('<p class="section-label">Métricas del portafolio de mínima varianza</p>',
                    unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        kpi(c1, "Volatilidad anual",  f"{portafolio['volatilidad']:.2f}%", "portafolio óptimo")
        kpi(c2, "Retorno esperado",   f"{portafolio['retorno']:.2f}%",     "anual estimado")
        kpi(c3, "Sharpe ratio",       f"{portafolio['sharpe']:.3f}",       "sin tasa libre de riesgo")
        kpi(c4, "Monedas",            str(len(monedas_sel)),               "en el portafolio")

        st.markdown("<br>", unsafe_allow_html=True)

        # Pie + Frontera
        col_pie, col_front = st.columns([2, 3])
        with col_pie:
            st.markdown('<p class="section-label">Pesos óptimos</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(
                grafico_pesos_portafolio(portafolio["pesos"]),
                use_container_width=True,
            )

        with col_front:
            st.markdown('<p class="section-label">Frontera eficiente (Markowitz)</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(
                grafico_frontera_eficiente(
                    portafolio["frontera"],
                    portafolio["volatilidad"],
                    portafolio["retorno"],
                ),
                use_container_width=True,
            )

        # Tabla de pesos
        st.markdown('<p class="section-label">Detalle de pesos por moneda</p>',
                    unsafe_allow_html=True)
        df_pesos = pd.DataFrame([
            {
                "Moneda":    m,
                "Peso (%)":  round(p * 100, 2),
                "Volatilidad Anual (%)": metricas.loc[m, "Volatilidad Anual (%)"]
                    if m in metricas.index else "-",
                "Retorno Total (%)": metricas.loc[m, "Retorno Total (%)"]
                    if m in metricas.index else "-",
            }
            for m, p in portafolio["pesos"].items()
        ]).sort_values("Peso (%)", ascending=False).reset_index(drop=True)

        st.dataframe(df_pesos, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Datos
# ─────────────────────────────────────────────────────────────────────────────
with tab3:

    st.markdown('<p class="section-label">Métricas descriptivas por moneda</p>',
                unsafe_allow_html=True)
    st.dataframe(metricas, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Dataset filtrado</p>',
                unsafe_allow_html=True)

    # Control extra: filtro por moneda en tabla
    moneda_tabla = st.selectbox(
        "Filtrar tabla por moneda",
        options=["Todas"] + monedas_sel,
    )

    df_tabla = df if moneda_tabla == "Todas" else df[df["name"] == moneda_tabla]
    df_tabla = df_tabla.sort_values("date", ascending=False).reset_index(drop=True)

    st.dataframe(
        df_tabla[["name", "date", "open", "high", "low", "close", "volume", "market"]],
        use_container_width=True,
        height=400,
    )
    st.caption(f"Mostrando {len(df_tabla):,} de {len(df):,} registros.")
