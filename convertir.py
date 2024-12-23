# Abrir y decodificar el archivo UTF-16
with open('datos.json', 'r', encoding='utf-16') as file:
    content = file.read()

# Guardar el archivo limpio en UTF-8
with open('datos_clean.json', 'w', encoding='utf-8') as file:
    file.write(content)
