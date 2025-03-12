import pytest
import json
import boto3
import os
import csv
from unittest.mock import patch, MagicMock
from lambda2 import lambda_handler2, extraer_info_casas, guardar_csv

# 📌 Simulación de datos HTML con JSON-LD
HTML_SAMPLE = '''
<html>
    <head><script type="application/ld+json">
    [{
        "about": [
            {
                "address": {"addressLocality": "Centro"},
                "description": "Precio $300000",
                "numberOfBedrooms": 3,
                "numberOfBathroomsTotal": 2,
                "floorSize": {"value": 120}
            }
        ]
    }]
    </script></head>
    <body></body>
</html>
'''

@pytest.fixture
def mock_s3():
    """Mock para el cliente de S3"""
    with patch("boto3.client") as mock:
        s3_client = MagicMock()
        mock.return_value = s3_client
        yield s3_client

def test_lambda_handler2(mock_s3):
    """Prueba la descarga de HTML desde S3 y procesamiento de datos."""
    mock_s3.get_object.return_value = {"Body": MagicMock(read=lambda: HTML_SAMPLE.encode("utf-8"))}

    event = {
        "Records": [{"s3": {"object": {"key": "landing-casas/2025-03-11.html"}}}]
    }
    context = {}

    response = lambda_handler2(event, context)
    
    assert response["statusCode"] == 200
    assert "Archivo CSV guardado" in response["body"]

def test_extraer_info_casas():
    """Prueba la extracción de información de casas desde HTML."""
    datos = extraer_info_casas(HTML_SAMPLE, "2025-03-12")
    
    assert len(datos) == 1
    assert datos[0] == ["2025-03-12", "Centro", "300000", 3, 2, 120]

def test_guardar_csv():
    """Prueba que el CSV se genera correctamente."""
    ruta = "/tmp/test_output.csv"
    datos = [["2025-03-12", "Centro", "300000", 3, 2, 120]]

    guardar_csv(ruta, datos)

    assert os.path.exists(ruta)

    with open(ruta, newline="", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        assert reader[0] == ["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"]
        assert reader[1] == ["2025-03-12", "Centro", "300000", "3", "2", "120"]

