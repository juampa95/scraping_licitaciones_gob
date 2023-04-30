import os
import json
import pandas as pd

data = []
# Ruta a la carpeta que contiene los archivos JSON
folder_path = 'C:/Users/jpman/PycharmProjects/scraping_licitaciones_gob/Data'

# Bucle para recorrer cada archivo JSON en la carpeta
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        # Abre cada archivo y agrega sus datos a la lista 'data'
        with open(os.path.join(folder_path, filename)) as f:
            data.extend(json.load(f))

# Guarda la lista 'data' en un archivo JSON
with open('datos.json', 'w') as f:
    json.dump(data, f)

with open('datos.json') as f:
    datos = json.load(f)

df = pd.json_normalize(datos)

df.shape