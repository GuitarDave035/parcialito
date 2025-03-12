import pytest
from unittest.mock import patch, MagicMock
from lambda1 import lambda_handler

# 🔹 1️⃣ Prueba cuando todo funciona bien
@patch("boto3.client")
@patch("requests.get")
def test_lambda_handler_success(mock_requests_get, mock_boto):
    """Verifica que la lambda funcione correctamente cuando no hay errores."""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.text = "<html>OK</html>"
    
    s3_mock = MagicMock()
    mock_boto.return_value = s3_mock

    event = {}
    context = {}

    response = lambda_handler(event, context)

    assert response["status"] == "success"
    s3_mock.put_object.assert_called_once()  # 🔹 Confirma que S3 fue llamado

# 🔹 2️⃣ Prueba cuando falla la subida a S3
@patch("boto3.client")
@patch("requests.get")
def test_lambda_handler_s3_fail(mock_requests_get, mock_boto):
    """Simula un fallo en S3 y verifica que la lambda maneje el error."""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.text = "<html>OK</html>"

    s3_mock = MagicMock()
    s3_mock.put_object.side_effect = Exception("Error en S3")  # 🔹 Simulando fallo en S3
    mock_boto.return_value = s3_mock

    event = {}
    context = {}

    response = lambda_handler(event, context)

    assert response["status"] == "error"
    assert "Error en S3" in response["message"]

# 🔹 3️⃣ Prueba cuando NO se pueden descargar páginas (todas fallan)
@patch("boto3.client")
@patch("requests.get")
def test_lambda_handler_no_pages(mock_requests_get, mock_boto):
    """Simula un fallo en la descarga de todas las páginas."""
    mock_requests_get.return_value.status_code = 500  # 🔹 Todas las solicitudes fallan

    s3_mock = MagicMock()
    mock_boto.return_value = s3_mock

    event = {}
    context = {}

    response = lambda_handler(event, context)

    assert response["status"] == "error"
    assert "No se descargó ninguna página" in response["message"]
    s3_mock.put_object.assert_not_called()  # 🔹 No debe intentar subir a S3
