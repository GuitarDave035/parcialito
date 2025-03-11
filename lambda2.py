import json
import csv
import boto3
import datetime
from bs4 import BeautifulSoup

# Configuración de los buckets
SOURCE_BUCKET = "parcial11"  # Bucket donde está el HTML
SOURCE_PREFIX = "landing-casas/"  # Prefijo del HTML en el bucket
DEST_BUCKET = "casasfinalcsv"  # Bucket donde se guardará el CSV

# Cliente de S3
s3 = boto3.client("s3")

def lambda_handler2(event, context):
    print("🚀 Lambda ejecutado para procesar archivo HTML.")

    # Si el evento no tiene 'Records', se ejecuta manualmente
    if "Records" not in event:
        print("⚠️ Ejecución manual detectada. Usando fecha actual.")
        fecha_actual = datetime.datetime.today().strftime("%Y-%m-%d")
        archivo_html = f"{SOURCE_PREFIX}{fecha_actual}.html"
    else:
        # Obtener la clave del archivo subido desde el evento de S3
        registro = event["Records"][0]
        archivo_html = registro["s3"]["object"]["key"]
        fecha_actual = archivo_html.split("/")[-1].replace(".html", "")

    archivo_csv = f"{fecha_actual}.csv"

    try:
        # Descargar el archivo HTML desde S3
        print(f"📥 Descargando {archivo_html} desde {SOURCE_BUCKET}")
        response = s3.get_object(Bucket=SOURCE_BUCKET, Key=archivo_html)
        html_content = response["Body"].read().decode("utf-8")

        # Extraer la información usando BeautifulSoup
        casas_data = extraer_info_casas(html_content, fecha_actual)

        # Guardar la información en un archivo CSV
        ruta_local_csv = f"/tmp/{archivo_csv}"  # Lambda solo puede escribir en /tmp/
        guardar_csv(ruta_local_csv, casas_data)

        # Subir el archivo CSV a S3
        print(f"📤 Subiendo {archivo_csv} a {DEST_BUCKET}")
        s3.upload_file(ruta_local_csv, DEST_BUCKET, archivo_csv)

        print("✅ Proceso finalizado con éxito.")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Archivo CSV guardado en s3://{DEST_BUCKET}/{archivo_csv}"),
        }

    except Exception as e:
        print(f"❌ Error en el procesamiento: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}

