from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import pandas as pd
import io

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

