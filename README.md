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


API

Podemos realizar predicciones utilizando la API, accediendo a http://localhost:8800/.

Para hacer una predicción, debemos enviar una solicitud al endpoint Predict con un cuerpo de tipo JSON que contenga un campo de características (features) con cada entrada para el modelo.

Un ejemplo del json sería:



{

                'gender':'Female',

                'customer_type': 'Loyal customer',

                'age': 40,

                'type_of_travel': 'Personal Travel',

                'class_cus': 'Business',

                'flight_distance': 400,

                'inflight_wifi_service': 4,

                'departure_arrival_time_convenient': 4,

                'ease_of_online_booking':4,

                'gate_location':4,

                'food_and_drink':4,

                'online_boarding':4,

                'seat_comfort':4,

                'inflight_entertainment':4,

                'on_board_service':4,

                'leg_room_service':4,

                'baggage_handling':4,

                'checkin_service':4,

                'inflight_service':4,

                'cleanliness':4,

                'departure_delay_in_minutes':0,

                'arrival_delay_in_minutes':0



                }



La respuesta del modelo será un valor booleano y un mensaje en forma de cadena de texto que indicará si el usuario se encontrará o no satisfecho con el servicio brindado por la aerolínea.