from fastapi import FastAPI, HTTPException
import json
import pandas as pd
import os

app = FastAPI()

# Ruta del archivo Excel
EXCEL_PATH = r"C:\Users\javii\OneDrive\Escritorio\Excel ocaso\contactos (2).xlsx"

@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}

@app.post("/guardar-excel")
def guardar_datos_en_excel(datos: str):
    try:
        datos_dict = json.loads(datos)

        if not os.path.exists(EXCEL_PATH):
            return {"status": "error", "message": "El archivo Excel no se encontró."}

        df = pd.read_excel(EXCEL_PATH)

        nuevo_df = pd.DataFrame([datos_dict])
        df = pd.concat([df, nuevo_df], ignore_index=True)

        df.to_excel(EXCEL_PATH, index=False)

        return {"status": "success", "archivo": EXCEL_PATH}

    except PermissionError:
        raise HTTPException(status_code=500, detail="No se puede acceder al archivo Excel. Ciérralo si está abierto.")
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Error en el formato de los datos. Asegúrate de enviarlos como JSON válido.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desconocido: {str(e)}")
