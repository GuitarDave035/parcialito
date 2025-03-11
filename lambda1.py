import requests
import boto3
import datetime

BASE_URL = "https://casas.mitula.com.co/find?operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29"
S3_BUCKET = "parcial11"
s3 = boto3.client('s3', region_name='us-east-1')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

def download_page(url: str) -> str:
    print(f"Descargando URL: {url}")  # ✅ Depuración
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {url}: {e}")
        return None

def upload_to_s3(content: str, filename: str):
    print(f"Subiendo {filename} a S3...")  # ✅ Depuración
    try:
        s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=content)
        print(f"✅ Archivo {filename} subido exitosamente.")
    except Exception as e:
        print(f"❌ Error al subir a S3: {e}")

def lambda_handler(event, context):
    print("🚀 Lambda ejecutado")  # ✅ Depuración
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    filename = f"landing-casas/{today}.html"  # 📂 Ahora se guarda en la carpeta "landing-casas/"

    content = download_page(BASE_URL)
    if content:
        upload_to_s3(content, filename)
    
    print("✅ Proceso finalizado.")
    return {"statusCode": 200, "body": "Página descargada y subida a S3 correctamente"}