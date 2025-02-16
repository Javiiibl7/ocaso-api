from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Modelo de datos esperado
class DatosEmpresa(BaseModel):
    Nombre: str
    Dirección: str
    Teléfono: str
    Correo_electronico: str

# Almacenar datos en memoria (temporal)
datos_guardados = []

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}

@app.post("/guardar-excel")
def guardar_datos_en_excel(datos: DatosEmpresa):
    datos_guardados.append(datos.dict())  # Guardar datos en memoria
    return {"status": "success", "message": "Datos guardados temporalmente en la API"}

@app.get("/descargar-excel")
def descargar_excel():
    if not datos_guardados:
        raise HTTPException(status_code=404, detail="No hay datos guardados")

    df = pd.DataFrame(datos_guardados)
    
    # Crear archivo en memoria
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    # Enviar archivo al usuario
    headers = {
        'Content-Disposition': 'attachment; filename="datos_ocaso.xlsx"'
    }
    return Response(output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

@app.get("/extraer-info")
def extraer_info(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="No se pudo acceder a la página")

        soup = BeautifulSoup(response.text, "html.parser")

        contacto = {
            "Nombre": soup.find("title").text if soup.find("title") else "No encontrado",
            "Teléfono": soup.find("a", href=True, text=True).text if soup.find("a", href=True, text=True) else "No encontrado",
            "Correo": "No encontrado",
            "Dirección": "No encontrado"
        }

        return contacto

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la extracción: {str(e)}")
