
def save_payload_to_file(payload, filepath_template, ext):
    filepath = filepath_template.format(ext=ext)
    
    if ext == "txt":
        # Convertir el payload a una representación de texto legible
        payload_text = str(payload)
        
        # Guardar en formato de texto
        with open(filepath, "a") as file:
            file.write(payload_text + "\n\n")
