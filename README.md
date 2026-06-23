# Crypto Portfolio Dashboard

Dashboard interactivo para analizar criptomonedas con datos históricos y datos live.
Combina una base histórica reproducible de CoinMarketCap/Kaggle con precios recientes
desde CoinGecko para comparar mercado pasado vs. mercado actual.

Desarrollado como **Entrega Parcial** del curso
*Programación Avanzada para la Ciencia de Datos* - UP 2026.

---

## Estructura del repositorio

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

## Datos usados

### 1. Base histórica

El análisis principal usa `data/crypto-markets.csv`, una base histórica y estable.
Esto permite que el dashboard funcione incluso sin conexión a internet.

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

### 2. Datos live

La pestaña **Live CoinGecko** consulta la API pública de CoinGecko para traer:

- Precio actual en USD
- Cambio porcentual de 24 horas
- Volumen de 24 horas
- Market cap actual
- Series recientes de 30 o 90 días

Nota: CoinGecko puede devolver `HTTP Error 429: Too Many Requests` si se hacen
muchas consultas seguidas. No significa que el código esté mal; significa que la
API pública limitó temporalmente las solicitudes. En ese caso, espera unos minutos
y pulsa **Actualizar precios**.

---

## Requisitos

- Python 3.10 o superior
- Git
- Conexión a internet solo para la pestaña Live CoinGecko

---

## Cómo ejecutar localmente

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

# Si PowerShell bloquea la activación, ejecutar:
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

Si el puerto está ocupado:

```bash
streamlit run src/app.py --server.port 8502
```

---

## Funcionalidades del dashboard

### Pestaña Precios & Mercado
- KPIs por moneda (precio medio, retorno total, volatilidad)
- Evolución de precios con opción de escala logarítmica
- Velas japonesas (OHLC) por moneda
- Volumen diario de transacciones
- Volatilidad anual comparativa
- Distribución de retornos diarios
- Guía rápida para entender volatilidad, Sharpe, correlación y backtesting

### Pestaña Portafolio Óptimo
- Optimización de portafolio con perfiles de riesgo
- KPIs: volatilidad, retorno esperado y Sharpe ratio
- Pie chart con pesos óptimos por moneda
- Frontera eficiente con punto óptimo según perfil
- Tabla de pesos por moneda
- Heatmap de correlación entre monedas
- Backtesting de una inversión inicial
- Descarga del portafolio óptimo como CSV

### Pestaña Live CoinGecko
- Snapshot actual de precios desde CoinGecko
- Variación de 24 horas
- Volumen y market cap actual
- Gráfico de precios recientes de 30 o 90 días
- Portafolio óptimo usando datos recientes
- Comparación del mercado histórico vs. condiciones actuales

### Pestaña Datos
- Métricas descriptivas completas por moneda
- Tabla de datos filtrable por moneda y rango de fechas

### Controles disponibles
| Control | Tipo | Efecto |
|---|---|---|
| Criptomonedas | Multiselect | Filtra monedas en todos los gráficos |
| Actualizar precios | Botón | Limpia caché y vuelve a consultar CoinGecko |
| Ventana live | Radio | Cambia entre 30 y 90 días recientes |
| Tasa libre de riesgo | Number input | Recalcula el Sharpe ratio |
| Perfil de riesgo | Radio | Conservador, Balanceado o Agresivo |
| Simular inversión inicial | Number input | Monto usado en el backtesting |
| Rango de fechas | Date picker | Filtra el período de análisis |
| Escala logarítmica | Toggle | Cambia escala del gráfico de precios |
| Moneda individual | Selectbox | Elige moneda para velas, volumen e histograma |
| Filtro de tabla | Selectbox | Filtra la tabla de datos por moneda |

---

## Perfiles de riesgo

- **Conservador:** minimiza volatilidad. Busca reducir el riesgo total.
- **Balanceado:** maximiza Sharpe. Busca mejor retorno ajustado por riesgo.
- **Agresivo:** prioriza mayor retorno esperado. Puede asumir más riesgo.

---

## Ejecutar tests

Después de instalar dependencias:

```bash
pytest
```

Los tests verifican que los retornos no tengan valores faltantes y que los pesos
del portafolio sumen 1.

---

## Problemas frecuentes

### CoinGecko muestra HTTP Error 429

Es un límite temporal de la API pública. Soluciones:

1. Esperar unos minutos.
2. Pulsar **Actualizar precios**.
3. Seleccionar menos monedas.
4. Seguir usando las pestañas históricas, que no dependen de internet.

### Streamlit no abre en localhost:8501

Prueba otro puerto:

```bash
streamlit run src/app.py --server.port 8502
```

### PowerShell no activa el entorno virtual

Ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

---

## Equipo

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

## Uso de IA

Este proyecto utilizó **Claude (Anthropic, claude-sonnet-4-6)** para:
- Scaffolding inicial de los módulos `processing.py`, `viz.py` y `app.py`
- Sugerencias de estructura del repositorio y estilos visuales

El equipo revisó, adaptó y es responsable de todo el código final.
