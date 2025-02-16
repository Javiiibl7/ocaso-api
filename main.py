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
