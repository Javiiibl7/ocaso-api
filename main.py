from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup
import validators
import re

# Definir la aplicación
app = FastAPI()

# Modelo de datos para almacenar en Excel
class DatosEmpresa(BaseModel):
    Nombre: str
    Dirección: str
    Teléfono: str
    Correo_electronico: str

# Almacenar datos en memoria temporalmente
datos_guardados = []

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}

@app.post("/guardar-excel")
def guardar_datos_en_excel(datos: DatosEmpresa):
    datos_guardados.append(datos.dict())
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

    headers = {
        'Content-Disposition': 'attachment; filename="datos_ocaso.xlsx"'
    }
    return Response(output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

# ✅ Función para limpiar y validar URL
def limpiar_url(url: str) -> str:
    url = url.strip()
    url = re.sub(r'[\"\']', '', url)  # Eliminar comillas dobles y simples
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="URL inválida")
    return url

@app.get("/extraer-info")
def extraer_info(url: str):
    try:
        url = limpiar_url(url)  # Limpiar y validar la URL

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/",
            "DNT": "1"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Error {response.status_code}: No se pudo acceder a la página")

        soup = BeautifulSoup(response.text, "html.parser")

        # Extraer título de la página
        nombre = soup.find("title").text.strip() if soup.find("title") else "No encontrado"

        # Buscar teléfonos en enlaces <a href="tel:">
        telefono = "No encontrado"
        for link in soup.find_all("a", href=True):
            if "tel:" in link["href"]:
                telefono = link.text.strip()
                break

        # Buscar correos electrónicos en enlaces <a href="mailto:">
        correo = "No encontrado"
        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:
                correo = link.text.strip()
                break

        # Intentar extraer dirección desde etiquetas <p>, <span>, <div>
        direccion = "No encontrado"
        for etiqueta in ["p", "span", "div"]:
            for elemento in soup.find_all(etiqueta):
                texto = elemento.get_text(strip=True)
                if re.search(r"(Calle|Avda|Dirección|Plaza|Paseo|Mallorca)", texto, re.IGNORECASE):
                    direccion = texto
                    break

        return {
            "Nombre": nombre,
            "Teléfono": telefono,
            "Correo": correo,
            "Dirección": direccion
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error en la extracción: {str(e)}")

# ✅ Modelo de datos para generación de mensajes
class MensajeRequest(BaseModel):
    actividad: str

@app.post("/generar-mensaje")
def generar_mensaje(request: MensajeRequest):
    try:
        mensajes = {
            "inmobiliaria": "Estimado cliente, queremos ofrecerle nuestro seguro especializado para inmobiliarias...",
            "gestoria": "Como gestor, sabemos la importancia de proteger su negocio. Le ofrecemos una solución...",
            "asesoria": "En su labor de asesor, contar con un seguro adecuado es fundamental. Le proponemos...",
            "default": "Estimado cliente, tenemos una oferta especial para usted."
        }

        mensaje = mensajes.get(request.actividad.lower(), mensajes["default"])

        return {"mensaje": mensaje}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el mensaje: {str(e)}")
