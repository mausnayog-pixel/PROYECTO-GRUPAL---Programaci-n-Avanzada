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
    obtener_precios_coingecko,
    obtener_market_chart_coingecko,
    calcular_backtest_portafolio,
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
    grafico_live_precios,
    grafico_correlacion,
    grafico_backtest,
)

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Portfolio Dashboard",
    page_icon="B",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

:root {
    --bg: #050403;
    --panel: rgba(18, 17, 16, 0.88);
    --panel-strong: rgba(27, 25, 23, 0.96);
    --stroke: rgba(255, 255, 255, 0.12);
    --text: #FFF8F1;
    --muted: #A7A09A;
    --accent: #FF5A1F;
    --accent-2: #FFB067;
    --good: #23F2A0;
}

html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif;
    color: var(--text);
}

::-webkit-scrollbar {
    width: 13px;
    height: 13px;
}

::-webkit-scrollbar-track {
    background: #0A0807;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
    border: 3px solid #0A0807;
    border-radius: 999px;
}

header[data-testid="stHeader"] {
    background: rgba(5, 4, 3, 0.94);
    border-bottom: 1px solid rgba(255, 255, 255, 0.10);
}

.stApp {
    background:
        radial-gradient(circle at 66% -10%, rgba(255, 90, 31, 0.30), transparent 34rem),
        radial-gradient(circle at 96% 38%, rgba(255, 176, 103, 0.20), transparent 24rem),
        linear-gradient(180deg, #060504 0%, #0A0604 48%, #030303 100%);
}

section[data-testid="stSidebar"] {
    background: rgba(4, 4, 4, 0.94);
    border-right: 1px solid var(--stroke);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.3rem;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

.hero {
    position: relative;
    overflow: hidden;
    display: grid;
    grid-template-columns: minmax(0, 1fr) 360px;
    gap: 1.25rem;
    align-items: stretch;
    min-height: 430px;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 1.6rem;
    background:
        radial-gradient(ellipse at 42% 22%, rgba(255, 90, 31, 0.52), transparent 31%),
        radial-gradient(ellipse at 72% 54%, rgba(255, 176, 103, 0.18), transparent 34%),
        linear-gradient(135deg, rgba(37, 34, 31, 0.92), rgba(3, 3, 3, 0.98));
    box-shadow: 0 28px 90px rgba(0, 0, 0, 0.50);
}

.hero:before,
.hero:after {
    content: "";
    position: absolute;
    border-radius: 999px;
    pointer-events: none;
}

.hero:before {
    width: 860px;
    height: 310px;
    left: 24%;
    top: 1rem;
    transform: rotate(-8deg);
    border: 1px solid rgba(255, 127, 64, 0.28);
    box-shadow: 0 0 70px rgba(255, 90, 31, 0.30), inset 0 0 42px rgba(255, 90, 31, 0.14);
}

.hero:after {
    width: 460px;
    height: 460px;
    right: -120px;
    bottom: -160px;
    background: radial-gradient(circle, rgba(255, 90, 31, 0.24), transparent 62%);
}

.hero-content {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-width: 0;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 2.1rem;
}

.brand-dot {
    width: 28px;
    height: 28px;
    display: inline-grid;
    place-items: center;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: white;
    font-family: 'Sora', sans-serif;
    font-weight: 800;
    box-shadow: 0 0 28px rgba(255, 77, 28, 0.75);
}

.brand-name {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #FFF8F1;
}

.hero-kicker {
    color: var(--accent-2);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
}

.hero h1 {
    max-width: 820px;
    font-family: 'Sora', sans-serif;
    font-size: clamp(2.35rem, 5vw, 5.1rem);
    line-height: 0.98;
    letter-spacing: 0;
    margin: 0;
    color: var(--text);
}

.hero p {
    max-width: 640px;
    margin: 1.15rem 0 1.35rem;
    color: #D6CEC6;
    font-size: 1.02rem;
    line-height: 1.65;
}

.hero-actions {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
}

.pill {
    display: inline-flex;
    align-items: center;
    min-height: 38px;
    border-radius: 999px;
    padding: 0.55rem 0.9rem;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid var(--stroke);
    color: #D8D0C8;
    font-size: 0.82rem;
    font-weight: 700;
}

.pill-hot {
    color: white;
    background: linear-gradient(135deg, var(--accent), #FF6A28);
    border-color: transparent;
    box-shadow: 0 12px 34px rgba(255, 77, 28, 0.34);
}

.floating-card {
    position: static;
    z-index: 3;
    width: auto;
    border-radius: 8px;
    padding: 1.1rem;
    background: linear-gradient(145deg, rgba(37, 36, 35, 0.86), rgba(12, 12, 12, 0.90));
    border: 1px solid var(--stroke);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.42);
    backdrop-filter: blur(18px);
}

.hero-side {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-rows: 1fr 1fr;
    gap: 1rem;
    min-width: 0;
}

.float-label {
    color: var(--muted);
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 0.7rem;
}

.float-value {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 700;
}

.spark {
    height: 86px;
    margin-top: 1rem;
    border-radius: 8px;
    background:
        linear-gradient(135deg, transparent 14%, rgba(255, 90, 31, 0.30) 15% 22%, transparent 23%),
        linear-gradient(160deg, transparent 25%, rgba(255, 255, 255, 0.44) 26% 30%, transparent 31%),
        radial-gradient(circle at 86% 62%, rgba(255, 90, 31, 0.95), transparent 0.34rem),
        linear-gradient(180deg, rgba(255, 77, 28, 0.12), rgba(255, 77, 28, 0));
}

.coin-row {
    display: flex;
    justify-content: space-between;
    gap: 0.6rem;
    margin-top: 0.6rem;
    color: #DCD6CF;
    font-size: 0.94rem;
    font-weight: 700;
}

.coin-row span:last-child { color: var(--good); }

section[data-testid="stSidebar"] div[data-baseweb="select"],
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"],
section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
section[data-testid="stSidebar"] input {
    background: #141312 !important;
    border: 1px solid var(--stroke) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    color: #F7F2EC !important;
}

section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"],
section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
    min-height: 118px !important;
    align-items: flex-start !important;
}

section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] * {
    scrollbar-width: none;
}

section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] *::-webkit-scrollbar {
    width: 0;
    height: 0;
}

section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    min-height: 48px !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background: linear-gradient(135deg, var(--accent), #FF6A28);
    border-radius: 7px;
}

.stMultiSelect [data-baseweb="tag"] span,
.stMultiSelect [data-baseweb="tag"] svg {
    color: white !important;
}

.stToggle label,
.stSelectbox label,
.stMultiSelect label,
.stDateInput label {
    color: #B8B0A8 !important;
}

.kpi-card {
    background: linear-gradient(145deg, rgba(34, 34, 34, 0.84), rgba(12, 12, 12, 0.88));
    border-radius: 8px;
    padding: 1.1rem 1rem;
    min-height: 122px;
    border: 1px solid var(--stroke);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 16px 35px rgba(0,0,0,0.25);
}

.kpi-card .kpi-label {
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: var(--muted);
    margin-bottom: 0.55rem;
}

.kpi-card .kpi-value {
    font-family: 'Sora', sans-serif;
    font-size: 1.65rem;
    line-height: 1;
    font-weight: 700;
    color: var(--text);
}

.kpi-card .kpi-sub {
    font-size: 0.72rem;
    color: #B8B0A8;
    margin-top: 0.65rem;
}

.section-label {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-family: 'Sora', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--accent-2);
    margin: 1.1rem 0 0.8rem;
}

.section-label:before {
    content: "";
    width: 30px;
    height: 1px;
    background: linear-gradient(90deg, var(--accent), transparent);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.55rem;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 999px;
    padding: 0 1rem;
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--stroke);
    font-family: 'Sora', sans-serif;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), #FF6E2E);
    border-color: transparent;
    color: white;
}

div[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border: 1px solid var(--stroke);
    border-radius: 8px;
    background: rgba(17, 17, 17, 0.72);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.26);
}

button[kind="primary"],
.stButton > button {
    border-radius: 999px;
    background: linear-gradient(135deg, var(--accent), #FF7A2D) !important;
    border: 0 !important;
    color: white !important;
    font-weight: 800 !important;
    box-shadow: 0 12px 28px rgba(255, 90, 31, 0.26);
}

.stButton > button:hover {
    filter: brightness(1.08);
    color: white !important;
}

@media (max-width: 900px) {
    .hero { grid-template-columns: 1fr; min-height: auto; padding: 1.2rem; }
    .hero-side { grid-template-columns: 1fr; }
    .hero h1 { font-size: 2.35rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-content">
        <div>
            <div class="brand-row">
                <span class="brand-dot">B</span>
                <span class="brand-name">Cryptox Portfolio</span>
            </div>
            <div class="hero-kicker">Crypto intelligence dashboard</div>
            <h1>Analiza El Futuro Del Crypto Trading</h1>
            <p>Explora precios historicos, volatilidad y portafolios optimizados con una vista clara para tomar mejores decisiones.</p>
        </div>
        <div class="hero-actions">
            <span class="pill pill-hot">Mercado 2013-2018</span>
            <span class="pill">Top crypto assets</span>
            <span class="pill">Portfolio analytics</span>
        </div>
    </div>
    <div class="hero-side">
        <div class="floating-card">
            <div class="float-label">Market signal</div>
            <div class="float-value">$15.4K</div>
            <div class="spark"></div>
        </div>
        <div class="floating-card">
            <div class="float-label">Crypto exchange</div>
            <div class="coin-row"><span>BTC</span><span>+12.4%</span></div>
            <div class="coin-row"><span>ETH</span><span>+8.7%</span></div>
            <div class="coin-row"><span>LTC</span><span>+5.3%</span></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Carga de datos (cacheada) ─────────────────────────────────────────────────
RUTA_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "crypto-markets.csv")

@st.cache_data(show_spinner="Cargando datos...")
def obtener_datos(monedas: tuple) -> pd.DataFrame:
    df_raw = cargar_datos(RUTA_CSV)
    return limpiar_datos(df_raw, monedas=list(monedas))

@st.cache_data(show_spinner="Optimizando portafolio...")
def obtener_portafolio(monedas: tuple, tasa_libre_riesgo: float, perfil_riesgo: str):
    df = obtener_datos(monedas)
    retornos = calcular_retornos(df)
    return optimizar_portafolio(
        retornos,
        tasa_libre_riesgo=tasa_libre_riesgo,
        perfil_riesgo=perfil_riesgo,
    )

@st.cache_data(show_spinner="Consultando CoinGecko...")
def obtener_live_snapshot(monedas: tuple) -> pd.DataFrame:
    return obtener_precios_coingecko(list(monedas))

@st.cache_data(show_spinner="Descargando precios recientes de CoinGecko...")
def obtener_live_chart(monedas: tuple, dias: int) -> pd.DataFrame:
    return obtener_market_chart_coingecko(list(monedas), dias=dias)

# ── Sidebar ───────────────────────────────────────────────────────────────────
if "monedas_sel" not in st.session_state:
    st.session_state["monedas_sel"] = TOP5_DEFAULT.copy()

def restaurar_monedas_default():
    st.session_state["monedas_sel"] = TOP5_DEFAULT.copy()

def guia_rapida():
    with st.expander("Guia rapida para entender estos indicadores"):
        st.markdown("""
        - **Volatilidad:** mide que tan brusco se mueve el precio. Mas volatilidad implica mas riesgo.
        - **Sharpe:** compara retorno contra riesgo. Si sube, el portafolio compensa mejor el riesgo asumido.
        - **Correlacion:** muestra si dos monedas se mueven parecido. Baja correlacion ayuda a diversificar.
        - **Frontera eficiente:** combinaciones de monedas que buscan mejor retorno para cada nivel de riesgo.
        - **Backtesting:** simula cuanto valdria una inversion inicial siguiendo la estrategia seleccionada.
        """)

with st.sidebar:
    st.markdown("### Trading Desk")
    st.markdown("---")

    # Control 1: selección de monedas
    monedas_sel = st.multiselect(
        "Criptomonedas",
        options=TOP5_DEFAULT,
        key="monedas_sel",
        help="Elige las monedas para analizar y construir el portafolio.",
    )

    if not monedas_sel:
        st.warning("Selecciona al menos una moneda.")
        st.button(
            "Restaurar monedas",
            use_container_width=True,
            on_click=restaurar_monedas_default,
        )
        st.stop()

    st.markdown("---")

    if st.button("Actualizar precios", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    dias_live = st.radio(
        "Ventana live",
        options=[30, 90],
        index=0,
        format_func=lambda x: f"{x} dias",
        horizontal=True,
        help="CoinGecko entrega precios recientes para comparar contra el historico.",
    )

    tasa_libre_riesgo = st.number_input(
        "Tasa libre de riesgo anual (%)",
        min_value=0.0,
        max_value=25.0,
        value=4.5,
        step=0.25,
        help="Se descuenta del retorno esperado para recalcular el Sharpe.",
    )

    perfil_riesgo = st.radio(
        "Perfil de riesgo",
        options=["Conservador", "Balanceado", "Agresivo"],
        index=0,
        help=(
            "Conservador minimiza volatilidad, Balanceado busca mejor Sharpe "
            "y Agresivo prioriza retorno esperado."
        ),
    )

    inversion_inicial = st.number_input(
        "Simular inversion inicial (USD)",
        min_value=100.0,
        max_value=1_000_000.0,
        value=1000.0,
        step=100.0,
        help="Monto usado para el backtesting del portafolio y monedas.",
    )

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
    st.caption("Programacion Avanzada · 2025")

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
    portafolio = obtener_portafolio(tuple(monedas_sel), tasa_libre_riesgo, perfil_riesgo)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab_live, tab3 = st.tabs([
    "Precios & Mercado",
    "Portafolio Optimo",
    "Live CoinGecko",
    "Datos",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Precios & Mercado
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    guia_rapida()

    # KPIs
    st.markdown('<p class="section-label">Indicadores clave del período</p>',
                unsafe_allow_html=True)

    def fmt_usd(v):
        if pd.isna(v):
            return "-"
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
    guia_rapida()

    if not hay_portafolio:
        st.info("Selecciona al menos 2 monedas en el panel lateral para calcular el portafolio óptimo.")
    else:
        # KPIs del portafolio
        st.markdown(f'<p class="section-label">Métricas del portafolio {perfil_riesgo.lower()}</p>',
                    unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        kpi(c1, "Volatilidad anual",  f"{portafolio['volatilidad']:.2f}%", perfil_riesgo.lower())
        kpi(c2, "Retorno esperado",   f"{portafolio['retorno']:.2f}%",     "anual estimado")
        kpi(c3, "Sharpe ratio",       f"{portafolio['sharpe']:.3f}",       f"rf: {tasa_libre_riesgo:.2f}% anual")
        kpi(c4, "Monedas",            str(len(monedas_sel)),               "en el portafolio")
        kpi(c5, "Simulacion",          fmt_usd(inversion_inicial),          "monto inicial")

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
                            nombre_punto=f"Perfil {perfil_riesgo}",
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

        st.download_button(
            "Descargar portafolio CSV",
            data=df_pesos.to_csv(index=False).encode("utf-8"),
            file_name="portafolio_optimo.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_corr, col_backtest = st.columns(2)
        retornos_hist = calcular_retornos(df)
        with col_corr:
            st.markdown('<p class="section-label">Correlacion entre monedas</p>',
                        unsafe_allow_html=True)
            st.plotly_chart(grafico_correlacion(retornos_hist), use_container_width=True)

        with col_backtest:
            st.markdown('<p class="section-label">Backtesting del portafolio</p>',
                        unsafe_allow_html=True)
            df_backtest = calcular_backtest_portafolio(df, portafolio["pesos"], inversion_inicial)
            if df_backtest.empty:
                st.info("No hay datos suficientes para simular el backtesting.")
            else:
                st.plotly_chart(grafico_backtest(df_backtest), use_container_width=True)
                ultimo_valor = (
                    df_backtest[df_backtest["Serie"] == "Portafolio optimo"]
                    .sort_values("date")
                    .tail(1)["Valor"]
                )
                if not ultimo_valor.empty:
                    valor_final = float(ultimo_valor.iloc[0])
                    ganancia = valor_final - inversion_inicial
                    st.caption(
                        f"Con {fmt_usd(inversion_inicial)} iniciales, el perfil {perfil_riesgo.lower()} "
                        f"terminaria en {fmt_usd(valor_final)} ({ganancia:+,.2f} USD)."
                    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Live CoinGecko
# ─────────────────────────────────────────────────────────────────────────────
with tab_live:
    st.markdown('<p class="section-label">Mercado live via CoinGecko</p>',
                unsafe_allow_html=True)

    live_snapshot = pd.DataFrame()
    try:
        live_snapshot = obtener_live_snapshot(tuple(monedas_sel))
    except Exception as exc:
        st.warning("CoinGecko limito o rechazo el snapshot actual. Prueba Actualizar precios en unos segundos.")
        st.caption(f"Detalle tecnico: {exc}")

    if live_snapshot.empty:
        st.info("Aun no hay snapshot live disponible para las monedas seleccionadas.")
    else:
        live_cols = st.columns(len(live_snapshot))
        for i, row in live_snapshot.reset_index(drop=True).iterrows():
            cambio = row["change_24h"]
            signo = "+" if pd.notna(cambio) and cambio >= 0 else ""
            cambio_txt = f"{signo}{cambio:.2f}%" if pd.notna(cambio) else "-"
            kpi(
                live_cols[i],
                row["name"],
                fmt_usd(row["price"]),
                f"24h: {cambio_txt} | Vol: {fmt_usd(row['volume_24h'])}",
            )

        ultima_actualizacion = live_snapshot["last_updated"].dropna()
        if not ultima_actualizacion.empty:
            st.caption(
                "Ultima actualizacion CoinGecko: "
                f"{ultima_actualizacion.max().strftime('%Y-%m-%d %H:%M UTC')}"
            )

    st.markdown("<br>", unsafe_allow_html=True)
    try:
        live_chart = obtener_live_chart(tuple(monedas_sel), dias_live)
    except Exception as exc:
        live_chart = pd.DataFrame()
        st.warning("CoinGecko limito la descarga de series recientes. El snapshot puede seguir disponible.")
        st.caption(f"Detalle tecnico: {exc}")

    if live_chart.empty:
        st.info("No se pudo construir la serie reciente desde CoinGecko.")
    else:
        st.plotly_chart(
            grafico_live_precios(live_chart, monedas_sel),
            use_container_width=True,
        )

        if len(monedas_sel) >= 2:
            retornos_live = calcular_retornos(live_chart)
            if retornos_live.empty:
                st.info("No hay suficientes retornos live para optimizar el portafolio.")
            else:
                portafolio_live = optimizar_portafolio(
                    retornos_live,
                    tasa_libre_riesgo=tasa_libre_riesgo,
                    perfil_riesgo=perfil_riesgo,
                )
                st.markdown('<p class="section-label">Portafolio optimo live</p>',
                            unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                kpi(c1, "Volatilidad live", f"{portafolio_live['volatilidad']:.2f}%", f"ultimos {dias_live} dias")
                kpi(c2, "Retorno live", f"{portafolio_live['retorno']:.2f}%", "anualizado")
                kpi(c3, "Sharpe live", f"{portafolio_live['sharpe']:.3f}", f"rf: {tasa_libre_riesgo:.2f}%")

                col_l1, col_l2 = st.columns([2, 3])
                with col_l1:
                    st.plotly_chart(
                        grafico_pesos_portafolio(portafolio_live["pesos"]),
                        use_container_width=True,
                    )
                with col_l2:
                    st.plotly_chart(
                        grafico_frontera_eficiente(
                            portafolio_live["frontera"],
                            portafolio_live["volatilidad"],
                            portafolio_live["retorno"],
                            nombre_punto=f"Live {perfil_riesgo}",
                        ),
                        use_container_width=True,
                    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Datos
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
