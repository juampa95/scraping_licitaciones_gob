import pandas as pd

# Estas lineas son para ver el dataframe
with open('Data/23042023multi.json', 'r') as f:
    datos = pd.read_json(f)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
datos.head()

# No hay ninguno duplicado.

datos['NumProcesoIndice'].duplicated().sum()

datos.describe(include='all').T['freq'].sort_values(ascending=False)[0:30]