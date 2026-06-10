# 🪙 Crypto Portafolio Dashboard

Dashboard interactivo para el análisis de precios históricos de criptomonedas 
y optimización de portafolio de mínima varianza (Teoría de Markowitz).

Desarrollado como **Entrega Parcial** del curso
*Programación Avanzada para la Ciencia de Datos* — UP 2026.

---

## 📁 Estructura del repositorio

```
ProyectoProgramación/
├── data/
│   └── crypto-markets.csv       # Dataset histórico de criptomonedas
├── src/
│   ├── app.py                   # Entrada principal de Streamlit
│   ├── processing.py            # Carga, limpieza, métricas y optimización
│   └── viz.py                   # Funciones de graficación (Plotly)
├── docs/
│   └── parcial.pdf              # Documento de entrega parcial
├── requirements.txt             # Dependencias del proyecto
└── README.md
```

---

## 🗂️ Dataset

| Campo       | Tipo    | Descripción                              |
|-------------|---------|------------------------------------------|
| `name`      | string  | Nombre de la criptomoneda                |
| `symbol`    | string  | Símbolo (BTC, ETH, etc.)                 |
| `date`      | date    | Fecha del registro                       |
| `open`      | float   | Precio de apertura (USD)                 |
| `high`      | float   | Precio máximo del día (USD)              |
| `low`       | float   | Precio mínimo del día (USD)              |
| `close`     | float   | Precio de cierre (USD)                   |
| `volume`    | float   | Volumen de transacciones (USD)           |
| `market`    | float   | Capitalización de mercado (USD)          |

**Fuente:** CoinMarketCap Historical Data via Kaggle
**URL:** https://www.kaggle.com/datasets/jessevent/all-crypto-currencies
**Licencia:** CC0 — Public Domain
**Período:** Abril 2013 – Noviembre 2018
**Monedas analizadas:** Bitcoin, Ethereum, Litecoin, Dash, Monero

---

## 🚀 Cómo ejecutar localmente

### 1. Clonar el repositorio
```bash
git clone https://github.com/mausnayog-pixel/PROYECTO-GRUPAL---Programaci-n-Avanzada.git
cd PROYECTO-GRUPAL---Programaci-n-Avanzada
```

### 2. Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Si da error de permisos, ejecutar
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Lanzar la aplicación
```bash
streamlit run src/app.py
```

La app se abrirá automáticamente en **http://localhost:8501**

---

## 🖥️ Funcionalidades del dashboard

### Pestaña 📈 Precios & Mercado
- KPIs por moneda (precio medio, retorno total, volatilidad)
- Evolución de precios con opción de escala logarítmica
- Velas japonesas (OHLC) por moneda
- Volumen diario de transacciones
- Volatilidad anual comparativa
- Distribución de retornos diarios

### Pestaña 🏦 Portafolio Óptimo
- Portafolio de mínima varianza (Markowitz)
- KPIs: volatilidad, retorno esperado y Sharpe ratio
- Pie chart con pesos óptimos por moneda
- Frontera eficiente con punto óptimo marcado
- Tabla de pesos por moneda

### Pestaña 📋 Datos
- Métricas descriptivas completas por moneda
- Tabla de datos filtrable por moneda y rango de fechas

### Controles disponibles
| Control | Tipo | Efecto |
|---|---|---|
| Criptomonedas | Multiselect | Filtra monedas en todos los gráficos |
| Rango de fechas | Date picker | Filtra el período de análisis |
| Escala logarítmica | Toggle | Cambia escala del gráfico de precios |
| Moneda individual | Selectbox | Elige moneda para velas, volumen e histograma |
| Filtro de tabla | Selectbox | Filtra la tabla de datos por moneda |

---

## 👥 Equipo

| Nombre | Correo |
|--------|--------|
| Marianela Usnayo Gutierrez| ma.usnayog@alum.up.edu.pe |
| Angie Uchuypoma Romero | am.uchuypomar@alum.up.edu.pe |
| Rosa Ortiz Palomino | rl.ortizp@alum.up.edu.pe |
| Karin Gadeo Liza | correo4@alum.up.edu.pe |

**Curso:** Programación Avanzada para la Ciencia de Datos
**Sección:** A
**Fecha:** 2026-1

---

## 🤖 Uso de IA

Este proyecto utilizó **Claude (Anthropic, claude-sonnet-4-6)** para:
- Scaffolding inicial de los módulos `processing.py`, `viz.py` y `app.py`
- Sugerencias de estructura del repositorio y estilos visuales

El equipo revisó, adaptó y es responsable de todo el código final.
