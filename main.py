from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Modelo para los datos extraídos
class EmpresaInfo(BaseModel):
    Nombre: str
    Dirección: Optional[str] = None
    Teléfono: Optional[str] = None
    Correo_electronico: Optional[str] = None
    Sitio_web: Optional[str] = None
    Redes_Sociales: Optional[str] = None
    Contacto_Principal: Optional[str] = None
    Fecha_de_Contacto: Optional[str] = None

# Ruta para extraer información desde una URL
@app.post("/extraer-info")
def extraer_info(url: str = Query(...)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ejemplo de extracción de correo
        correos = [text for text in soup.stripped_strings if '@' in text]
        
        return {
            "Nombre": "Empresa Ejemplo",
            "Correo electrónico": correos[0] if correos else "No encontrado",
            "Sitio web": url,
            "Fecha de Contacto": "2025-02-09"
        }
    except Exception as e:
        return {"Error": f"No se pudo extraer la información: {e}"}

# Correr la API localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
