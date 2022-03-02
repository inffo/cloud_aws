Introducción

El objetivo es comprender las demoras de los vuelos  diarios en distintos aeropuertos a lo largo de los años. 
Para realizar esto, se busca transformar datos crudos de demora de varios años de vuelos, almacenados en S3, a datos procesados almacenados en una base de datos para finalmente poder pasarlos a una herramienta de visualización y así obtener un mejor entendimiento de los mismos.

Resumen Pipeline:

El sistema crea un pipeline para obtener datos de s3, realizar un preprocesamiento de datos y cargarlos en una instancia RDS Postgres.
Esta tarea se orquesta con Airflow y se implementa dentro de un contenedor Docker en EC2.
Finalmente, los datos procesados son visualizados en un dashboard en Quicksight para sacar conclusiones de forma más fácil.


Como fue realizado:

Los datos crudos se almacenaron en s3 descargandolos de kaggle y siguiendo los pasos de las instrucciones.
Una instancia ec2 fue usada para levantar un Docker con Airflow. En ella un dag fue creado con el objetivo de leer los datos, procesarlos para obtener los outliers de delay por dia y origen, escribir los datos en rds y crear visualizaciones para subir a s3.
Una instancia de RDS postgres fue creada para almacenar los datos procesados.
Quicksight es utilizado para visualizar los mismos datos que se subieron a RDS. Y poder armar un dashboard donde visualizar fácilmente el análisis.


Detalles:

Para la utilización de Airflow, una imagen de Docker con Airflow fue descargada y usada como base para extenderla con librerías propias necesarias para el procesamiento de datos.
Una task de python fue creada en un Dag para obtener datos de S3 , realizar el procesamiento y subirlos a RDS.
SQL alchemy y Pandas fue usado para lograr eso.

Airflow:
El dag fue realizado con una función que toma un parámetro como input con el nombre del archivo para el año que se desea analizar.
Este parámetro debe pasarse al inciar el dag, ya sea programáticamente o mediante la UI de Airflow.

Por ejemplo si quiero pasarle el archivo para analizar el año 2017:
{"year_csv":"s3://airline-outliers/2017.csv"}


 “year_csv” debe ser el key, y el value debe ser el nombre del archivo a analizar. Cualquiera desde 2009 hasta 2018 que está actualmente en el bucket de S3.


Para poner en funcionamiento el sistema:

Levantar los servicios mediante el comando: docker-compose up.
Ir a localhost:8080 para ver el UI Airflow.
Correr el dag “dag_flights” with parameters: 

	Cualquiera de los archivos con los datos crudos en s3 bucket airplane-outliers:
El key:value a pasar como parámetro es cualquiera de :
{"year_csv":"s3://airline-outliers/2009.csv"}
{"year_csv":"s3://airline-outliers/2010.csv"}
{"year_csv":"s3://airline-outliers/2011.csv"}
{"year_csv":"s3://airline-outliers/2012.csv"}
{"year_csv":"s3://airline-outliers/2013.csv"}
{"year_csv":"s3://airline-outliers/2014.csv"}
{"year_csv":"s3://airline-outliers/2015.csv"}
{"year_csv":"s3://airline-outliers/2016.csv"}
{"year_csv":"s3://airline-outliers/2017.csv"}
{"year_csv":"s3://airline-outliers/2018.csv"}

Ahí se ejecuta el Dag y realiza toda la tarea, dejando los plots en s3 en el directorio airplane-outliers/plots, subiendo los archivos procesados a rds, y dejandolos también en s3 en el directorio airplane-outliers/dataframes.


Recursos utilizados:


S3 Bucket

Bucket Airplane-outliers:
Datos crudos de vuelos para los años desde 2009 a 2018

Directory /plot:
Plots para los diferentes “Origin” de los vuelos en los distintos años.
Los plots realizados por el procesamiento de datos para analizar outliers. Se realizó un pdf por año, donde cada uno contiene un plot de cada ORIGIN mostrando la media de demora de vuelos por día.

	
Directory /dataframes
	Los mismos datos que fueron subidos a la base de datos en RDS fue almacenado en este bucket de S3. Esto fue realizado con el objetivo de poder descargar los datos como csv y asi poder subirlos manualmente a Quicksight. Este no es el objetivo final, ya que queremos que Quicksight este conectado directamente a RDS y no tener que hacer este trabajo manualmente, pero no logré hacerlo, probablemente, por motivos de permisos.

EC2 

Se desarrollaron los archivos que se encuentran en el respositorio, y fue usada como cómputo para poder correr docker , airflow y los archivos python que realizan las tareas necesarias para el procesamiento.


	Archivos :

Dockerfile 
Usada para extender la imagen básica de Airflow Docker con libraries necesarias para procesar los datos.

Docker-compose.yml
Para levantar los servicios necesarios para que corra Airflow dentro del docker.
Requirements.txt: librerías para ser instaladas dentro de docker.

Debajo del directorio /dags:

Dag_flights.py:

Dag de Airflow que realiza lo siguiente:

Toma la entrada del parámetro que se le otorgue, que es el nombre del archivo del csv que se leerá desde s3.
Lee datos de s3.
Calcula valores por día y origen y obtiene outliers:
(Primero agrupa por día y origen, calcula la media de los retrasos y etiqueta como outliers a los que están por encima del percentil 90).
Crea gráficos de retrasos de vuelos por día y origen y los carga en S3.
Carga datos en RDS Postgres.
Se utilizó SQL Alchemy y pandas.
Sube los dataframes tambien a un directorio de S3.



RDS:

Una base de datos Postgres fue implementada para almacenar los datos procesados. El paso siguiente es poder visualizarlos siendo conectados con una herramienta como Quicksight.




Quicksight:

	Visualización de los datos procesados. 
	El objetivo era conectar los datos directamente desde la base de datos en RDS pero no lo logré. Creo yo que era por motivos de permisos de la lab. Por esa razón, los mismos datos que cargue en RDS los cargué en S3 como archivos csv en el directorio Airlines-outliers/dataframes. Y de esa forma descargué uno de los archivos, año 2012, para subirlo como csv a quicksight y poder armar una visualización. 
Para poner en producción, es necesario conectar quicksight a rds. Para esto, hay que establecer permisos en RDS para poder leer datos desde quicksight. Se debe crear un rol con estos permisos.


Mejoras a implementar:

Desarmar el dag en varias tasks. Actualmente una task realiza todo el trabajo que conceptualmente debe ser 3. Leer datos de S3, hacer el procesamiento y calculo de outliers , y escribir los datos a rds.


El dag está programado para correr de forma anual. Pero es necesario, actualmente, insertar el parámetro del archivo que queremos que lea de S3. El objetivo es cambiar esto para hacer que una vez por año, si no se le pasa ningún parámetro con archivo, agarre el último archivo subido al bucket (que corresponde al nuevo año) y se ejecute el task. 

Conectar quicksight a rds directo.
Mejorar dashboard de Quicksight con visualizaciones que permitan obtener mejores insights.
