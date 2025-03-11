import json
import csv
import boto3
import datetime
from bs4 import BeautifulSoup

# Configuración de los buckets
SOURCE_BUCKET = "parcial11"  # 📌 Bucket donde está el HTML
SOURCE_PREFIX = "landing-casas/"  # 📌 Prefijo del HTML en el bucket
DEST_BUCKET = "casasfinalcsv"  # 📌 Bucket donde se guardará el CSV

# Cliente de S3
s3 = boto3.client("s3")

def lambda_handler2(event, context):
    print("🚀 Lambda ejecutado para procesar archivo HTML.")

    fecha_actual = datetime.datetime.today().strftime("%Y-%m-%d")  # 📌 Fecha actual por defecto
    archivo_html = f"{SOURCE_PREFIX}{fecha_actual}.html"  # 📌 Ruta por defecto en el bucket

    # 📌 Verificar si el evento proviene de S3
    if "Records" in event and len(event["Records"]) > 0:
        try:
            registro = event["Records"][0]
            archivo_html = registro["s3"]["object"]["key"]
            fecha_actual = archivo_html.split("/")[-1].replace(".html", "")  # Extraer fecha del archivo
        except KeyError:
            print("⚠️ Estructura del evento incorrecta. Usando fecha actual.")
    
    archivo_csv = f"{fecha_actual}.csv"  # 📌 Nombre del CSV de salida

    try:
        # 📌 Descargar el archivo HTML desde S3
        print(f"📥 Descargando {archivo_html} desde {SOURCE_BUCKET}...")
        response = s3.get_object(Bucket=SOURCE_BUCKET, Key=archivo_html)
        html_content = response["Body"].read().decode("utf-8")

        # 📌 Extraer la información usando BeautifulSoup
        casas_data = extraer_info_casas(html_content, fecha_actual)

        # 📌 Guardar la información en un archivo CSV
        ruta_local_csv = f"/tmp/{archivo_csv}"  # Lambda solo puede escribir en /tmp/
        guardar_csv(ruta_local_csv, casas_data)

        # 📌 Subir el archivo CSV a S3
        print(f"📤 Subiendo {archivo_csv} a {DEST_BUCKET}...")
        s3.upload_file(ruta_local_csv, DEST_BUCKET, archivo_csv)

        print("✅ Proceso finalizado con éxito.")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Archivo CSV guardado en s3://{DEST_BUCKET}/{archivo_csv}"),
        }

    except Exception as e:
        print(f"❌ Error en el procesamiento: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}

def extraer_info_casas(html_content, fecha_descarga):
    """Extrae la información de las casas desde el JSON-LD en el HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    casas = []

    # Buscar la etiqueta <script> que contiene el JSON-LD
    json_ld_script = soup.find("script", type="application/ld+json")
    
    if not json_ld_script:
        print("❌ No se encontró la etiqueta JSON-LD en el HTML.")
        return []

    try:
        json_data = json.loads(json_ld_script.string)
        propiedades = json_data[0]["about"]  # Lista de casas en el JSON-LD

        for propiedad in propiedades[:10]:  # Tomar solo los primeros 10 resultados
            barrio = propiedad["address"].get("addressLocality", "Desconocido")
            valor = propiedad.get("description", "No disponible").split("$")[-1].split(" ")[0]  # Extrae precio
            num_habitaciones = propiedad.get("numberOfBedrooms", "0")
            num_banos = propiedad.get("numberOfBathroomsTotal", "0")
            mts2 = propiedad["floorSize"].get("value", "0")

            casas.append([fecha_descarga, barrio, valor, num_habitaciones, num_banos, mts2])
        
        print(f"📊 Se extrajeron {len(casas)} casas.")

    except Exception as e:
        print(f"⚠️ Error procesando JSON-LD: {e}")

    return casas

def guardar_csv(ruta, datos):
    """Guarda la información en un archivo CSV."""
    try:
        with open(ruta, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
            writer.writerows(datos)
        print(f"✅ CSV guardado en {ruta}")
    except Exception as e:
        print(f"❌ Error guardando CSV: {e}")
