## WEB SCRAPER CON SELENIUM 
La idea de este proyecto es recolectar información sobre licitaciones 
públicas desde la página COMPRAR. En ella el gobierno ofrece todos los datos
sobre licitaciones adjudicadas y en proceso. 

Mediante esta información se intentara desarrollar un modelo para detectar 
patrones en ellas, como el precio ganador, demora de adjudicacion, empresas preferidas, etc.

> La elección de selenium como herramienta para recolectar datos se debio a 
> que la página "COMPRAR" utiliza JavaScript, limitando el uso de otras herramientas 
> mas poderosas o rapidas como Scrapy. 

### Versión 1.0

En una primera instancia, se creó el script [Scraper.py](Scraper.py) en donde 
raspaba los datos de una lista de licitaciones una a una. Si bien funcionó, era
demasiado lento.

Con este se obtuvo información de algunas licitaciones. Que puede
observarse en el archivo json llamado datos_iniciales.

### Versión 2.0 

En una instancia posterior, decidí indagar en la ejecución de procesos multi hilo.
Esto me llevo a conocer módulos como concurrent.futures u threading junto con sus 
clases principales ThreadPoolExecutor y Lock.
Con ellas fue posible hacer el proceso de raspado mucho mas rapido y eficiente, dando
la posibilidad de ejecutar varios procesos al mismo tiempo en los diferentes
hilos de mi procesador. 

Esto trajo nuevos desafíos, ya que ejecutar varios procesos en un mismo pc puede
generar problemas de concurrencia o condiciones de carrera.

-   Problemas de concurrencia: varios procesos intentan acceder al mismo elemento en 
un mismo momento. Esto puede generar el bloqueo del archivo o la sobrescritura de datos.
-   Problemas de condiciones de carrera: varios procesos compiten por los recursos del PC.
Esto genera que algunos procesos no tengan recursos y queden detenidos. 

Para evitar estos problemas, se utilizó la libreria threading que permite crear un bloqueo
a los archivos y recursos cuando un proceso los está utilizando, liberándolo una vez terminado. 
Por otro lado, con ThreadPoolExecutor podemos crear procesos en multiples hilos de manear concurrente. 

El código completo de esta version multi-hilo del scraper en selenium utilizado sobre una web JavaScript
puede verse en el archivo [ScraperMultiThread.py](ScraperMultiThread.py).

Los resultados arrojados por este, son compatibles con la Versión 1.0

Para acceder a una pequeña muestra de los datos obtenidos pueden ingresar al archivo haciendo click
en el link: [muestra.json](muestra.json) o pueden buscar el archivo [datos_iniciales.json](datos_iniciales.json)
que deberán descargar, ya que es demasiado grande para visualizarlo en github.

El archivo final con todos los datos recolectados tiene un tamaño de mas de 130 MB.
Conteniendo información sobre 55.823 procesos licitatorios, con una cantidad de 520 columnas.

### Proximos pasos

-[x] Analizar datos, detectar nulos y ver si es posible o necesario volver a raspar esos procesos

-[ ] Determinar el objetivo del proyecto. Que quiero predecir, con que exactitud y en función de esto
definir que tipo de modelos voy a utilizar y con que métricas los voy a evaluar. 

-[ ] Determinar de que forma se van a splitear los datos. Cada proceso licitatorio cuenta con 
diferentes empresas que presentaron distintas ofertas para la misma licitación. En función de eso
podría transformar cada fila, obteniendo información sobre quien gano la licitación y quien no.
De esta forma puedo analizar, características, precios, etc. de ambos tipos de empresa.

-[ ] Entrenar modelos, medir resultados, optimizar hiperparámetros.

-[ ] Una vez que se tenga un MVP podemos volver a utilizar el scraper para obtener nuevos procesos 
licitatorios y comparar resultados para ver que tan exacto es nuestro modelo.

-[ ] En un futuro, dependiendo de que tipos de resultados arroje el modelo, será posible
obtener información de licitaciones en proceso, que aún no han sido adjudicadas, para predecir
el resultado de alguno de los parámetros.


---
El análisis inicial de datos se realizó en el archivo [joinjson.py](joinjson.py) en donde uní todos 
los json resultantes del scraper. Ya que tuve que dividir su ejecución en varios dias.

Al tener un archivo por día, fue necesario recolectarlos todos en un unico .json, para luego comprobar
si existían nulos o duplicados. Al parecer, al detener el proceso e iniciarlo al dia siguiente, algunos
registros se duplicaron. Por lo que fueron eliminados. 

