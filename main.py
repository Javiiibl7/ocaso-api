from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

# Ruta del archivo Excel donde se guardarán los datos
EXCEL_PATH = r"C:\Users\javii\OneDrive\Escritorio\Excel ocaso\contactos (2).xlsx"

# Modelo de datos esperado
class DatosEmpresa(BaseModel):
    Nombre: str
    Dirección: str
    Teléfono: str
    Correo_electronico: str

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}

@app.post("/guardar-excel")
def guardar_datos_en_excel(datos: DatosEmpresa):
    try:
        # Verificar si el archivo Excel existe
        if not os.path.exists(EXCEL_PATH):
            # Si no existe, crear un nuevo archivo con encabezados
            df = pd.DataFrame(columns=["Nombre", "Dirección", "Teléfono", "Correo electrónico"])
            df.to_excel(EXCEL_PATH, index=False)

        # Leer el archivo existente
        df = pd.read_excel(EXCEL_PATH)

        # Convertir los datos a DataFrame
        nuevo_df = pd.DataFrame([datos.dict()])

        # Agregar los nuevos datos
        df = pd.concat([df, nuevo_df], ignore_index=True)

        # Guardar el archivo Excel
        df.to_excel(EXCEL_PATH, index=False)

        return {"status": "success", "archivo": EXCEL_PATH}

    except PermissionError:
        raise HTTPException(status_code=500, detail="No se puede acceder al archivo Excel. Ciérralo si está abierto.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desconocido: {str(e)}")
