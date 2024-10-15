"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import fastapi
import requests
import httpx


# Definir la función que hace una solicitud POST a FastAPI
async def predict(vars_dict):
    url = "http://fastapi:8800/predict/"
    async with httpx.AsyncClient() as client:
        # Hacer la solicitud POST enviando un JSON con los datos del item
        vars_dict = {"features": vars_dict}
        response = await client.post(url, json=vars_dict)
        if response.status_code == 200:
            return response.json()  # Devuelve el contenido JSON de la respuesta
        else:
            return {"error": f"Error: {response.status_code}"}


# Define la lógica de la encuesta
class Survey(rx.State):
    items: list[int] = [0, 1, 2, 3, 4, 5]
    name: str = ""
    gender: list[str] = ['Male', 'Female']
    gender_value: str = ''
    customer_type: list[str] = ['Loyal Customer', 'disloyal Customer']
    customer_type_value: str = ''
    age: int = 0
    type_of_travel: list[str] = ['Business travel', 'Personal Travel']  # "Propósito del vuelo para el pasajero",
    type_of_travel_value: str = ''
    class_cus: list[str] = ['Eco', 'Eco Plus', 'Business']  # "Clase en el vuelo a la que pertenece el pasajero",
    class_cus_value: str = ''
    flight_distance: int = 0  # "Distancia del vuelo",
    inflight_wifi_service: int = 0  # "Nivel de satisfacción con el servicio de wifi a bordo",
    departure_arrival_time_convenient: int = 0  # "Nivel de satisfacción de la hora de salida/llegada",
    ease_of_online_booking: int = 0  # "Nivel de satisfacción de la reserva online",
    gate_location: int = 0  # "Nivel de satisfacción con la ubicación de la puerta",
    food_and_drink: int = 0  # "Nivel de satisfacción con la comida y la bebida",
    online_boarding: int = 0  # "Nivel de satisfacción del embarque online",
    seat_comfort: int = 0  # "Nivel de satisfacción con la comodidad del asiento",
    inflight_entertainment: int = 0  # "Nivel de satisfacción con el servicio de entretenimiento a bordo",
    on_board_service: int = 0  # "Nivel de satisfacción con el servicio a bordo",
    leg_room_service: int = 0  # "Nivel de satisfacción con el espacio para las piernas",
    baggage_handling: int = 0  # "Nivel de satisfacción del manejo de equipaje",
    checkin_service: int = 0  # "Nivel de satisfacción con el servicio de check-in",
    inflight_service: int = 0  # "Nivel de satisfacción con el servicio en el vuelo",
    cleanliness: int = 0  # "Nivel de satisfacción con la limpieza",
    departure_delay_in_minutes: int = 0  # "Minutos de atraso en la salida",
    arrival_delay_in_minutes: int = 0  # "Minutos de atraso en el arribo",
    fer_result: str = ''

    async def submit(self):
        # Lógica para procesar las respuestas
        vars_dict = {
            'gender': self.gender_value,
            'customer_type': self.customer_type_value,
            'age': self.age,
            'type_of_travel': self.type_of_travel_value,
            'class_cus': self.class_cus_value,
            'flight_distance': self.flight_distance,
            'inflight_wifi_service': self.inflight_wifi_service,
            'departure_arrival_time_convenient': self.departure_arrival_time_convenient,
            'ease_of_online_booking': self.ease_of_online_booking,
            'gate_location': self.gate_location,
            'food_and_drink': self.food_and_drink,
            'online_boarding': self.online_boarding,
            'seat_comfort': self.seat_comfort,
            'inflight_entertainment': self.inflight_entertainment,
            'on_board_service': self.on_board_service,
            'leg_room_service': self.leg_room_service,
            'baggage_handling': self.baggage_handling,
            'checkin_service': self.checkin_service,
            'inflight_service': self.inflight_service,
            'cleanliness': self.cleanliness,
            'departure_delay_in_minutes': self.departure_delay_in_minutes,
            'arrival_delay_in_minutes': self.arrival_delay_in_minutes,
        }
        print(vars_dict)
        data = await predict(vars_dict)
        rx.toast(f"Predicción recibida: {data}")
        print(str(data))
        self.fer_result=data['str_output']
        print(f"Nombre: {self.name}, Pregunta 2: {self.age}, Pregunta 3: {self.on_board_service}")

def index() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.text("RESULTADO"),
                rx.heading(value=Survey.fer_result),
                rx.input(value=Survey.fer_result, on_blur=Survey.set_fer_result),
                rx.text("Ingrese su nombre por favor:"),
                rx.input(value=Survey.name, placeholder="Nombre", on_change=Survey.set_name),
                rx.text("Indique su genero"),
                rx.radio(
                    Survey.gender,
                    direction="row",
                    on_change=Survey.set_gender_value,
                ),
                rx.text("Indique su edad"),
                rx.input(value=Survey.age, placeholder="Edad", on_change=Survey.set_age),
                rx.text("Indique tipo de cliente"),
                rx.select(
                    Survey.customer_type,
                    value=Survey.customer_type_value,
                    placeholder="Tipo de cliente",
                    label="Cliente",
                    on_change=Survey.set_customer_type_value,
                ),
                rx.text("Indique tipo de viaje"),
                rx.select(
                    Survey.type_of_travel,
                    value=Survey.type_of_travel_value,
                    placeholder="Travel type",
                    lavel="Travel",
                    on_change=Survey.set_type_of_travel_value,
                ),
                rx.text("Indique clase de vuelo"),
                rx.select(
                    Survey.class_cus,
                    value=Survey.class_cus_value,
                    placeholder="Clase de vuelo",
                    lavel="Clase de vuelo",
                    on_change=Survey.set_class_cus_value,
                ),
                rx.text("Indique la distancia del viaje"),
                rx.input(value=Survey.flight_distance, placeholder="Distancia del viaje",
                         on_change=Survey.set_flight_distance),
                rx.text("Nivel de satisfacción con el servicio de wifi a bordo"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    on_change=Survey.set_inflight_wifi_service
                ),
                rx.text("Nivel de satisfacción de la hora de salida/llegada"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_departure_arrival_time_convenient
                ),
                rx.text("Nivel de satisfacción de la reserva online"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_ease_of_online_booking
                ),
                rx.text("Nivel de satisfacción con la ubicación de la puerta"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_gate_location
                ),
                rx.text("Nivel de satisfacción con la comida y la bebida"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_food_and_drink
                ),
                rx.text("Nivel de satisfacción del embarque online"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_online_boarding
                ),
                rx.text("Nivel de satisfacción con la comodidad del asiento"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_seat_comfort
                ),
                rx.text("Nivel de satisfacción con el servicio de entretenimiento a bordo"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_inflight_entertainment,
                ),
                rx.text("Nivel de satisfacción con el servicio a bordo"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_on_board_service,
                ),
                rx.text("Nivel de satisfacción con el espacio para las piernas"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_leg_room_service,
                ),
                rx.text("Nivel de satisfacción del manejo de equipaje"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_baggage_handling,
                ),
                rx.text("Nivel de satisfacción con el servicio de check-in"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_checkin_service,
                ),
                rx.text("Nivel de satisfacción con el servicio en el vuelo"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_inflight_service,
                ),
                rx.text("Nivel de satisfacción con la limpieza"),
                rx.radio(
                    Survey.items,
                    direction="row",
                    default_value=0,
                    on_change=Survey.set_cleanliness,
                ),
                rx.text("Ingrese los minutos de atraso en la salida"),
                rx.input(value=Survey.departure_delay_in_minutes, placeholder="Atraso Salida",
                         on_change=Survey.set_departure_delay_in_minutes),
                rx.text("Ingrese los minutos de atraso en el arribo"),
                rx.input(value=Survey.arrival_delay_in_minutes, placeholder="Atraso Arribo",
                         on_change=Survey.set_arrival_delay_in_minutes),
                rx.button("Enviar", on_click=Survey.submit)
            )
        ),
    )


app = rx.App()
app.add_page(index)
