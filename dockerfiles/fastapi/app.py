import json
import pickle
import boto3
import mlflow

import numpy as np
import pandas as pd

from typing import Literal
from fastapi import FastAPI, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing_extensions import Annotated

# For debug purpose
# import pydevd_pycharm
# pydevd_pycharm.settrace('172.17.0.1', port=5678, stdoutToServer=True, stderrToServer=True)

def load_model(model_name: str, alias: str):
    try:
        # Load the trained model from MLflow
        mlflow.set_tracking_uri('http://mlflow:5000')
        client_mlflow = mlflow.MlflowClient()

        model_data_mlflow = client_mlflow.get_model_version_by_alias(model_name, alias)
        model_ml = mlflow.sklearn.load_model(model_data_mlflow.source)

        version_model_ml = int(model_data_mlflow.version)
    except Exception as e:
        print('No hay un modelo registrado')

    return model_ml, version_model_ml

class ModelInput(BaseModel):
    gender: Literal['Male','Female'] = Field(
        description="Genero del cliente"
    )
    customer_type: Literal['Loyal Customer','disloyal Customer'] = Field(
        description="Tipo de cliente"
    )
    age: int = Field(
        description="Edad del cliente",
	    ge=7,
        le=110
    )
    type_of_travel: Literal['Business travel','Personal Travel'] = Field(
        description="Propósito del vuelo para el pasajero",
    )
    class_cus: Literal['Eco','Eco Plus', 'Business'] = Field(
        description="Clase en el vuelo a la que pertenece el pasajero",
    )
    flight_distance: int = Field(
        description="Distancia del vuelo",
	    ge=1,
        le=10000
    )
    inflight_wifi_service: int = Field(
        description="Nivel de satisfacción con el servicio de wifi a bordo",
	    ge=0,
        le=5
    )
    departure_arrival_time_convenient: int = Field(
        description="Nivel de satisfacción de la hora de salida/llegada",
	    ge=0,
        le=5
    )
    ease_of_online_booking: int = Field(
        description="Nivel de satisfacción de la reserva online",
	    ge=0,
        le=5
    )
    gate_location: int = Field(
        description="Nivel de satisfacción con la ubicación de la puerta",
	    ge=0,
        le=5
    )
    food_and_drink: int = Field(
        description="Nivel de satisfacción con la comida y la bebida",
	    ge=0,
        le=5
    )
    online_boarding: int = Field(
        description="Nivel de satisfacción del embarque online",
	    ge=0,
        le=5
    )
    seat_comfort: int = Field(
        description="Nivel de satisfacción con la comodidad del asiento",
	    ge=0,
        le=5
    )
    inflight_entertainment: int = Field(
        description="Nivel de satisfacción con el servicio de entretenimiento a bordo",
	    ge=0,
        le=5
    )
    on_board_service: int = Field(
        description="Nivel de satisfacción con el servicio a bordo",
	    ge=0,
        le=5
    )
    leg_room_service: int = Field(
        description="Nivel de satisfacción con el espacio para las piernas",
	    ge=0,
        le=5
    )
    baggage_handling: int = Field(
        description="Nivel de satisfacción del manejo de equipaje",
	    ge=0,
        le=5
    )
    checkin_service: int = Field(
        description="Nivel de satisfacción con el servicio de check-in",
	    ge=0,
        le=5
    )
    inflight_service: int = Field(
        description="Nivel de satisfacción con el servicio en el vuelo",
	    ge=0,
        le=5
    )
    cleanliness: int = Field(
        description="Nivel de satisfacción con la limpieza",
	    ge=0,
        le=5
    )
    departure_delay_in_minutes: int = Field(
        description="Minutos de atraso en la salida",
	    ge=0,
        le=2000
    )
    arrival_delay_in_minutes: int = Field(
        description="Minutos de atraso en el arribo",
	    ge=0,
        le=2000
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
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
            ]
        }
    }


class ModelOutput(BaseModel):
    """
    Output schema for the heart disease prediction model.

    This class defines the output fields returned by the heart disease prediction model along with their descriptions
    and possible values.

    :param int_output: Output of the model. True if the patient has a heart disease.
    :param str_output: Output of the model in string form. Can be "Healthy patient" or "Heart disease detected".
    """

    int_output: bool = Field(
        description="Output del modelo. 'true' si el usuario esta satisfecho",
    )
    str_output: Literal["Usuario no satisfecho", "Usuario satisfecho"] = Field(
        description="Output del modelo en formato string",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "int_output": True,
                    "str_output": "Usuario satisfecho",
                }
            ]
        }
    }


# Load the model before start
model, version_model = load_model("customer_satisfaction_model_prod", 'champion')

app = FastAPI()


@app.get("/")
async def read_root():
    """
    Root endpoint of the Heart Disease Detector API.

    This endpoint returns a JSON response with a welcome message to indicate that the API is running.
    """
    return JSONResponse(content=jsonable_encoder({"message": "Bienvenido al predictor de satisfaccion del usuario API"}))


@app.post("/predict/", response_model=ModelOutput)
def predict(
    features: Annotated[
        ModelInput,
        Body(embed=True),
    ],
    background_tasks: BackgroundTasks
):
    """
    Endpoint for predicting heart disease.

    This endpoint receives features related to a patient's health and predicts whether the patient has heart disease
    or not using a trained model. It returns the prediction result in both integer and string formats.
    """
    
    # Extract features from the request and convert them into a list and dictionary
    features_list = [*features.dict().values()]
    features_key = [*features.dict().keys()]

    # Convert features into a pandas DataFrame
    features_df = pd.DataFrame(np.array(features_list).reshape([1, -1]), columns=features_key)


    #Encodeamos la variable Class que tiene un ordenamiento implícito
    def encode_class(input_string):  
        return input_string.replace('Eco', '0').replace('Eco Plus', '2').replace('Business', '3')  

    features_df['class_cus'] = encode_class(features_df['class_cus']) 

    #Hacemos dummies de las variables categoricas
    features_df['gender_male'] = np.where(features_df['gender']=='Male',1,0)

    features_df['customer_type_disloyal_customer'] = np.where(features_df['customer_type']=='disloyal Customer',1,0)

    features_df['type_of_travel_personal_travel'] = np.where(features_df['type_of_travel']=='Personal Travel',1,0)

    #Imputamos missings a las variables
    features_df['arrival_delay_in_minutes'] = np.where(features_df['arrival_delay_in_minutes'].isnull(), features_df['departure_delay_in_minutes'], features_df['arrival_delay_in_minutes'])

    #Generamos features adicionales
    for i in ['inflight_wifi_service', 'departure_arrival_time_convenient',	'ease_of_online_booking', 'online_boarding']:
        features_df[f'{i}_rta0'] = np.where(features_df[i]==0,1,0)

    #Tratamiento de outliers
    for col in ['flight_distance', 'departure_delay_in_minutes', 'arrival_delay_in_minutes']:
            dict_q95 = {'flight_distance': 3376, 'departure_delay_in_minutes': 77, 'arrival_delay_in_minutes': 78}

            features_df[col]= np.where(int(features_df[col])>dict_q95[col], dict_q95[col], features_df[col])

    #Mantenemos en el dataset las features input del modelo
    features_input = ['age', 'class_cus', 'flight_distance', 'inflight_wifi_service',
    'departure_arrival_time_convenient', 'ease_of_online_booking',
    'gate_location', 'food_and_drink', 'online_boarding', 'seat_comfort',
    'inflight_entertainment', 'on_board_service', 'leg_room_service',
    'baggage_handling', 'checkin_service', 'inflight_service',
    'cleanliness', 'departure_delay_in_minutes', 'arrival_delay_in_minutes',
    'gender_male', 'customer_type_disloyal_customer',
    'type_of_travel_personal_travel', 'inflight_wifi_service_rta0',
    'departure_arrival_time_convenient_rta0', 'ease_of_online_booking_rta0',
    'online_boarding_rta0']
    
    features_df = features_df[features_input]
    features_df = features_df.to_numpy()
    # Predict usando el modelo 
    prediction = model.predict(features_df)

    # Convertimos la prediccion a formato string
    str_pred = "Usuario no satisfecho"
    if prediction[0] > 0.5:
        str_pred = "Usuario satisfecho"

    # Return the prediction result
    return ModelOutput(int_output=bool(prediction[0].item()), str_output=str_pred)
