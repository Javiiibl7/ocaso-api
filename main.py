from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

# Ruta del nuevo archivo Excel
EXCEL_PATH = r"C:\Users\javii\OneDrive\Escritorio\Excel ocaso\Nuevos contactos .xlsx"

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
        print(f"Intentando guardar datos: {datos}")  # 🔍 Depuración

        # Verificar si el archivo Excel existe
        if not os.path.exists(EXCEL_PATH):
            print("📂 Archivo Excel no encontrado, creándolo...")
            df = pd.DataFrame(columns=["Nombre", "Dirección", "Teléfono", "Correo electrónico"])
            df.to_excel(EXCEL_PATH, index=False)

        print("📖 Leyendo archivo Excel...")
        df = pd.read_excel(EXCEL_PATH)

        print(f"📄 Datos antes de agregar: {df}")  # 🔍 Ver los datos antes de agregar
        nuevo_df = pd.DataFrame([datos.dict()])
        df = pd.concat([df, nuevo_df], ignore_index=True)

        print(f"✅ Guardando nuevos datos en Excel...")
        df.to_excel(EXCEL_PATH, index=False)

        print(f"✔️ Datos guardados correctamente en {EXCEL_PATH}")

        return {"status": "success", "archivo": EXCEL_PATH}

    except PermissionError:
        print("❌ Error: No se puede escribir en el archivo. ¿Está abierto?")
        raise HTTPException(status_code=500, detail="No se puede acceder al archivo Excel. Ciérralo si está abierto.")

    except Exception as e:
        print(f"⚠️ Error desconocido: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error desconocido: {str(e)}")
