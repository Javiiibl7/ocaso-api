from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup

# Definir la aplicación antes de las rutas
app = FastAPI()

# Modelo de datos esperado para guardar en Excel
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

        # Extraer título de la página
        nombre = soup.find("title").text if soup.find("title") else "No encontrado"

        # Buscar enlaces que podrían ser teléfonos
        telefono = "No encontrado"
        for link in soup.find_all("a", href=True):
            if "tel:" in link["href"]:  # Busca enlaces con "tel:"
                telefono = link.text.strip()
                break

        # Buscar correos electrónicos
        correo = "No encontrado"
        for link in soup.find_all("a", href=True):
            if "mailto:" in link["href"]:  # Busca enlaces con "mailto:"
                correo = link.text.strip()
                break

        # Intentar extraer dirección desde etiquetas <p>, <span>, etc.
        direccion = "No encontrado"
        posibles_etiquetas = ["p", "span", "div"]
        for etiqueta in posibles_etiquetas:
            for elemento in soup.find_all(etiqueta):
                texto = elemento.get_text(strip=True)
                if "Calle" in texto or "Avda" in texto or "Mallorca" in texto or "Dirección" in texto:
                    direccion = texto
                    break

        contacto = {
            "Nombre": nombre,
            "Teléfono": telefono,
            "Correo": correo,
            "Dirección": direccion
        }

        return contacto

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la extracción: {str(e)}")

# ✅ CORRECCIÓN: Recibir la actividad en el cuerpo del `POST`
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

        # Convertimos la actividad a minúsculas para evitar errores
        mensaje = mensajes.get(request.actividad.lower(), mensajes["default"])

        return {"mensaje": mensaje}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el mensaje: {str(e)}")
