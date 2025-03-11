import json
import csv
import boto3
import datetime
from bs4 import BeautifulSoup

# Configuración de los buckets
SOURCE_BUCKET = "parcial11"  # Bucket donde se almacena la página HTML
DEST_BUCKET = "casasfinalcsv"  # Bucket donde se guardará el CSV

# Cliente de S3
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("🚀 Lambda ejecutado para procesar archivo HTML.")

    # Obtener la fecha del evento
    fecha_actual = datetime.datetime.today().strftime("%Y-%m-%d")
    archivo_html = f"landing-casas/{fecha_actual}.html"  # Ruta correcta del HTML en el bucket de origen
    archivo_csv = f"{fecha_actual}.csv"

    try:
        # Descargar el archivo HTML desde S3
        print(f"📥 Descargando {archivo_html} desde {SOURCE_BUCKET}")
        response = s3.get_object(Bucket=SOURCE_BUCKET, Key=archivo_html)
        html_content = response['Body'].read().decode('utf-8')
        
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
            'statusCode': 200,
            'body': json.dumps(f"Archivo CSV guardado en s3://{DEST_BUCKET}/{archivo_csv}")
        }
    
    except Exception as e:
        print(f"❌ Error en el procesamiento: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }

def extraer_info_casas(html, fecha_descarga):
    soup = BeautifulSoup(html, 'html.parser')
    casas = []
    
    # Encuentra todas las propiedades en la página
    for casa in soup.find_all('div', class_='listing'):  # Ajustar según la estructura real del HTML
        try:
            barrio = casa.find('span', class_='location').text.strip() if casa.find('span', class_='location') else "Desconocido"
            valor = casa.find('span', class_='price').text.strip() if casa.find('span', class_='price') else "No disponible"
            num_habitaciones = casa.find('span', class_='rooms').text.strip() if casa.find('span', class_='rooms') else "0"
            num_banos = casa.find('span', class_='bathrooms').text.strip() if casa.find('span', class_='bathrooms') else "0"
            mts2 = casa.find('span', class_='area').text.strip() if casa.find('span', class_='area') else "0"

            casas.append([fecha_descarga, barrio, valor, num_habitaciones, num_banos, mts2])
        
        except Exception as e:
            print(f"⚠️ Error procesando una casa: {e}")

    print(f"📊 Se extrajeron {len(casas)} casas.")
    return casas

def guardar_csv(ruta, datos):
    with open(ruta, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
        writer.writerows(datos)
    print(f"✅ Archivo CSV guardado en {ruta}")
