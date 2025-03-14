import boto3
import requests
import logging
from datetime import datetime
from urllib.parse import urlencode

# Configurar logging en lugar de print
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """Función principal de la Lambda."""
    bucket_name = "parcial11"  # Bucket de destino en S3
    base_url = "https://casas.mitula.com.co/find"
    s3 = boto3.client("s3")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    file_key = f"landing-casas/{today}.html"  # Nombre único del archivo por día
    all_pages_content = ""  # Acumulador del contenido HTML

    for page in range(1, 11):  # Descargar las primeras 10 páginas
        params = {
            "operationType": "sell",
            "propertyType": "mitula_studio_apartment",
            "geoId": "mitula-CO-poblacion-0000014156",
            "text": "Bogotá, (Cundinamarca)",
            "page": page,
        }
        url = f"{base_url}?{urlencode(params)}"

        try:
            response = requests.get(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
            )

            if response.status_code == 200:
                all_pages_content += f"\n<!-- Página {page} -->\n{response.text}"
                logger.info("✅ Página %d descargada correctamente.", page)
            else:
                logger.warning("⚠️ Error en página %d: %d", page, response.status_code)

        except requests.RequestException as req_err:
            logger.error("❌ Error en la solicitud de la página %d: %s", page, req_err)

    if not all_pages_content:
        logger.error("🚨 No se descargó ninguna página.")
        return {"status": "error", "message": "No se descargó ninguna página"}

    # Intentar subir a S3
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=all_pages_content.encode("utf-8"),
            ContentType="text/html",
        )
        logger.info("✅ Archivo guardado en S3: s3://%s/%s", bucket_name, file_key)
        return {"status": "success", "file": f"s3://{bucket_name}/{file_key}"}

    except boto3.exceptions.Boto3Error as s3_err:
        logger.error("🚨 Error al subir a S3: %s", s3_err)
        return {"status": "error", "message": str(s3_err)}
