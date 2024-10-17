AMq2 - CEIA - FIUBA

En este repositorio dejamos una implementación de un modelo productivo para detectar si un usuario se encontrará o no satisfecho con el servicio brindado por una aerolínea comercial. 

La implementación incluye:

En Apache Airflow, un DAG que obtiene los datos del repositorio, realiza limpieza y feature engineering, y guarda en el bucket s3://data los datos separados para entrenamiento y pruebas. 
Una notebook para ejecutar localmente con que entrena el modelo con los hiperparametros ya optimizados. Todo el experimento se registra en MLflow, se generan gráficos de importancia de features, y además, se registra el modelo en el registro de modelos de MLflow.
Un servicio de API del modelo, que toma el artefacto de MLflow y lo expone para realizar predicciones.


Testeo de Funcionamiento

El orden para probar el funcionamiento completo es el siguiente:

Ejecuta en Airflow el DAG llamado process_etl, de esta manera se crearán los datos en el bucket s3://data.
Ejecuta la notebook (ubicada en notebook_example) para entrenar el mejor modelo.
Utiliza el servicio de API.


Realizar Predicciones

Para llevar a cabo una predicción, se puede utilizar nuestra API. Para ello desarrollamos un frontend accesible en la siguiente ruta: http://localhost:3000/, donde se podrá introducir las características requeridas por el modelo y una vez completas las entradas, se realiza la predicción que indicará si el usuario se encontrará o no satisfecho con el servicio brindado por la aerolínea.
