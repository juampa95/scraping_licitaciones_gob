import time
import json
import pickle
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

df = pd.read_csv('D:/gitProyects/licitacionesEstatales-ds/ReporteProcesos.csv')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")
# final = pd.DataFrame()
# tiempos = pd.DataFrame(columns=['iteracion','tiempo_ejecucion'])
for iteracion in range(1000):
    # Vamos a hacer un diccionario, que tenga el valor del numero de proceso buscado por si el script falla
    n_proceso = {'NumProcesoIndice':df['Número de Proceso'][iteracion]}
    try:
        intentos = 0
        while intentos < 3:
            intentos += 1
            try:
                start_time = time.time()
                indice = df['Número de Proceso'][iteracion]
                driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")
                time.sleep(intentos)
                buscador = driver.find_element(By.ID, "ctl00_CPH1_txtNumeroProceso")
                time.sleep(intentos)
                buscador.send_keys(indice)
                time.sleep(intentos)
                driver.find_element(By.ID, "ctl00_CPH1_btnListarPliegoNumero").click()
                time.sleep(intentos+1)
                detalle = driver.find_element(By.XPATH, "//tbody/tr/td/a").click()
                time.sleep(intentos)
                titulos = driver.find_elements(By.XPATH, '//div[@class="col-md-4"]//label')
                break
            except:
                pass

        # una vez que tenemos todos los titulos, vamos a buscar los elementos /p/span
        # que contiene cada titulo. Este elemento es el texto debajo del titulo.

        datos = {}
        for i in range(len(titulos)):
            xpath = f'//div[label[contains(text(),"{titulos[i].text}")]]/p/span'
            texto = driver.find_elements(By.XPATH, xpath)
            pal = []
            for t in texto:
                if len(texto) == 1:
                    datos[titulos[i].text] = t.text
                else:
                    pal.append(t.text)
                    datos[titulos[i].text] = '. '.join(pal)

        # Obtenemos los datos del cronograma

        crono = {}
        cronograma_titulos = driver.find_elements(By.XPATH, '//div[div[h4[text()="Cronograma"]]]//label')
        cronograma_fechas = driver.find_elements(By.XPATH, '//div[div[h4[text()="Cronograma"]]]//p/span')
        try:
            for i in range(len(cronograma_titulos)):
                crono[cronograma_titulos[i].text] = cronograma_fechas[i].text
        except:
            pass

        # Obtenemos los datos tabulares

        h4 = driver.find_elements(By.XPATH, '//div/h4')
        dic_tablas = {}
        try:
            for h in h4:
                nomb_col = driver.find_elements(By.XPATH, f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//th')
                if len(nomb_col) != 0:
                    cant_filas = driver.find_elements(By.XPATH,
                                                      f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr')
                    filas_datos = {}
                    if len(cant_filas) != 1:
                        fila_datos = {}
                        for i in range(1, len(cant_filas) + 1):

                            valores_tablas = driver.find_elements(By.XPATH,
                                                                  f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr[{i}]/td')
                            for p in range(len(nomb_col)):
                                fila_datos[nomb_col[p].text + str(i)] = valores_tablas[p].text
                                fila_datos.update(fila_datos)
                            filas_datos = fila_datos
                    else:
                        fila_datos = {}
                        valores_tablas = driver.find_elements(By.XPATH,
                                                              f'//div[h4[text()="{h.text}"] and //table[thead and tbody]]//tbody//tr/td')
                        for j in range(len(nomb_col)):
                            fila_datos[nomb_col[j].text] = valores_tablas[j].text

                        filas_datos = fila_datos
                    dic_tablas[h.text] = filas_datos
        except:
            pass

        # AHORA VAMOS A TENER QUE HACER CLICK EN EL CUADRO COMPARATIVO PARA VER LOS PRECIOS QUE OFERTARON LOS COMPETIDORES
        time.sleep(1)
        try:
            driver.find_element(By.XPATH, '//div[a[@class="btn btn-link"]]/a').click()
            time.sleep(1)
            emp = driver.find_elements(By.XPATH, '//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-9"]/span')
            ofertas = driver.find_elements(By.XPATH, '//div[span[h4[text()="Mostrar ofertas"]]]//div[@class="col-md-3"]/span')
            empresas = []
            ofer = {}
            for i in emp:
                if i.text != "":
                    empresas.append(i.text)

            for i in range(len(ofertas)):
                ofer["empresa_oferente_" + str(i)] = empresas[i]
                ofer["monto_oferta_" + str(i)] = ofertas[i].text
        except:
            pass

        # unimos todo en un diccionario para luego concatenarlo en un dataframe
            # quiza no sea necesario esto. Podria guardar los diccionarios en pickles directamente

        dict_final = {}
        end_time = time.time()
        tiempo = {'tiempo_scraping':round(end_time-start_time,2)}
        for d in [n_proceso,tiempo,datos,crono,filas_datos,ofer]:
            dict_final.update(d)
        dict_list = [dict_final]
        # final = pd.concat([final,pd.DataFrame(dict_list)])
        # tiempos.loc[len(tiempos)] = [iteracion,(end_time-start_time)]
        # print(f'Iteracion N°: {iteracion} completada. Tiempo de ejecucion {end_time-start_time}segundos')
    except:
        dict_final = n_proceso

    # AGREGADO EN JSON LUEGO DE CADA ITERACION

    try:
        with open('datos.json', 'r') as f:
            datos_guardados = json.load(f)
    except FileNotFoundError:
        datos_guardados = []
        with open('datos.json', 'w') as f:
            json.dump(datos_guardados, f)
    datos_guardados.append(dict_final)

    with open('datos.json', "w") as f:
        json.dump(datos_guardados, f,ensure_ascii=False, indent=4)

    try:
        if iteracion % 100 == 0:
            print(f'...........[{iteracion/10}%] completado...................')
    except:
        pass

with open('datos.json', 'r') as f:
    datos = pd.read_json(f)

# Imprimir el DataFrame