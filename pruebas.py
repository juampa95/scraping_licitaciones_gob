import pandas as pd
import json
import os

# Estas lineas son para ver el dataframe
with open('Data/23042023multi.json', 'r') as f:
    datos = pd.read_json(f)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
datos.head()

# No hay ninguno duplicado.

datos['NumProcesoIndice'].duplicated().sum()

datos.describe(include='all').T['freq'].sort_values(ascending=False)[0:30]

with open('datos.json') as f:
    datos = json.load(f)

df = pd.json_normalize(datos)
df.shape
df.head()
df.duplicated(subset=['NumProcesoIndice'], keep=False).sum()

lic = df.copy()
lic = lic.drop_duplicates(subset=['NumProcesoIndice'], keep='first')

lic['tiempo_scraping'].isnull().sum()

nulos = lic[lic['tiempo_scraping'].isnull()]

nulos.shape

df.describe(include='all')

list(df.columns)

df.isnull().sum()

# Vamos a eliminar las columnas que contengan muchos valores nulos. Para determinar
# Que columnas quitaremos en un principio, vamos a considerar dejar aquellas columnas
# que tengan datos para el 99.99% de los registros
# El dataframe tiene 55823 registros, por lo que vamos a quitar aquellas columnas que
# no contengan datos en mas de 5 registros.

int(df.shape[0]*0.0001)

cols_to_drop = []
for col in df.columns:
    if df[col].count() < int(df.shape[0]*0.0001):
        cols_to_drop.append(col)

print(f'la cantidad de columnas a dropear según el criterio utilizado son: {len(cols_to_drop)}')
print('Si bien se reduce significativamente la cantidad de columnas, siguen siendo muchas')

# Se hará lo mismo, pero dejando solo columnas que contengan datos para el 99.9% de los registros

cols_to_drop = []
for col in df.columns:
    if df[col].count() < int(df.shape[0]*0.001):
        cols_to_drop.append(col)
print(f'la cantidad de columnas a dropear según el criterio utilizado son: {len(cols_to_drop)}')
print('Si bien se reduce significativamente la cantidad de columnas, siguen siendo muchas')

# Se hará lo mismo, pero dejando solo columnas que contengan datos para el 99.5% de los registros

cols_to_drop = []
for col in df.columns:
    if df[col].count() < int(df.shape[0]*0.005):
        cols_to_drop.append(col)

print(f'la cantidad de columnas a dropear según el criterio utilizado son: {len(cols_to_drop)}')
print(f'Podemos ver que si dejamos las columnas que no sean nulas para el 99.5% de los datos')
print(f'extraemos un {round((len(cols_to_drop)/df.shape[1])*100,2)}% de las columnas')

df2 = df.copy().drop(cols_to_drop, axis = 1)

df2.shape

# Al ejecutar estos comandos, quitamos la maxima cantidad de filas de un dataframe mostradas por pantalla
# por eso, a continuación, se resetea este parámetro a sus valores por defecto.

pd.set_option('display.max_rows', None)
df2.describe(include = 'all').T
pd.reset_option('display.max_rows')

# Vamos a sumar el monto de licitaciones que se le ha asignado a c/empresa.
# Pero antes tenemos que transformar los numeros que estan como STR con '.' y ','
df2['Monto'] = df2['Monto'].str.replace('.','').str.replace(',','.')
df2['Monto'] = pd.to_numeric(df2['Monto'])

sum_lic_asignadas = df2.groupby('Nombre proveedor')['Monto'].sum().reset_index()

# Aca podemos ver el resultado, pero al ser numeros tan grandes no se ve correcto. Lo pasaremos a millones
sum_lic_asignadas.sort_values(by = 'Monto',ascending=False).head(10)

# Dividimos por mil cada valor

sum_lic_asignadas['Monto'] = sum_lic_asignadas['Monto'].apply(lambda x : x/1000000)

sum_lic_asignadas
# Ademas se agrega que porcentaje del total de las licitaciones del periodo representa c/empresa.

tot_lic = df2['Monto'].sum()/1000000

sum_lic_asignadas['porcentaje_del_total'] = sum_lic_asignadas['Monto'].apply(lambda x : (x/tot_lic)*100)

sum_lic_asignadas.sort_values(by = 'Monto',ascending=False).head(50)
