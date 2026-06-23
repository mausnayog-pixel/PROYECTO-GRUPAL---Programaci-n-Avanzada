import pandas as pd

from src.processing import calcular_retornos, optimizar_portafolio


def test_retornos_no_tienen_nan_y_pesos_suman_uno():
    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2024-01-01", "2024-01-02", "2024-01-03",
            "2024-01-01", "2024-01-02", "2024-01-03",
        ]),
        "name": ["Bitcoin", "Bitcoin", "Bitcoin", "Ethereum", "Ethereum", "Ethereum"],
        "close": [100.0, 110.0, 121.0, 50.0, 52.0, 55.0],
    })

    retornos = calcular_retornos(df)
    assert not retornos.isna().any().any()

    portafolio = optimizar_portafolio(retornos, tasa_libre_riesgo=4.5)
    assert abs(sum(portafolio["pesos"].values()) - 1.0) < 0.001
