from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.post("/extraer-info")
def extraer_info(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        correos = [text for text in soup.stripped_strings if '@' in text]
        
        return {
            "Nombre": "Empresa Ejemplo",
            "Correo electrónico": correos[0] if correos else "No encontrado",
            "Sitio web": url
        }
    except Exception as e:
        return {"Error": f"No se pudo extraer la información: {e}"}
