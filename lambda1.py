import boto3
import requests
from datetime import datetime
from urllib.parse import urlencode

def lambda_handler(event, context):
    bucket_name = "parcial11"  # 📌 Bucket correcto
    base_url = "https://casas.mitula.com.co/find"
    s3 = boto3.client("s3")
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    file_key = f"landing-casas/{today}.html"  # 📌 Ruta única para el día
    
    all_pages_content = ""  # 📌 Almacenará todas las páginas en un solo HTML
    
    for page in range(1, 11):  # 🔹 Descargar las primeras 10 páginas
        params = {
            "operationType": "sell",
            "propertyType": "mitula_studio_apartment",
            "geoId": "mitula-CO-poblacion-0000014156",
            "text": "Bogotá,  (Cundinamarca)",
            "page": page
        }
        url = f"{base_url}?{urlencode(params)}"
        
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code == 200:
            all_pages_content += f"\n<!-- Página {page} -->\n" + response.text
            print(f"✅ Descargada página {page}")
        else:
            print(f"❌ Error al descargar {url}: {response.status_code}")
    
    if all_pages_content:
        # 📌 Guardar todo en un único archivo HTML
        s3.put_object(
            Bucket=bucket_name, 
            Key=file_key, 
            Body=all_pages_content.encode("utf-8"), 
            ContentType="text/html"
        )
        print(f"✅ Archivo guardado: s3://{bucket_name}/{file_key}")
    
    return {"status": "success"}
