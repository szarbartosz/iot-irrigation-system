import json
import mosquitto
from geopy.geocoders import Nominatim
import ssl
import certifi
import geopy.geocoders


def prepare_sensors(sensorsArr, sectorsNo):
    for i in range(sectorsNo):
        sensorId = input(f"Podaj id sensora w sektorze {i + 1}: ")
        sensorsArr.append(sensorId)

def prepare_sprinklers(sprinklersArr, sectorsNo):
    for i in range(sectorsNo):
        sprinklersNo = int(input(f"Podaj liczbę zraszaczy w sektorze {i + 1}: "))

        for j in range(sprinklersNo):
            sprinklersArr.append([])
            sprinklersArr[i].append(input(f"Podaj id zraszacza nr.{j + 1} w sektorze {i + 1}: "))


def prepare_humidity_data(humidityArr, sectorsNo):
    for i in range(sectorsNo):
        humidity = int(input(f"Podaj pożądaną wilgotność w sektorze {i + 1} [%]: "))
        humidityArr.append(humidity)


def assemble_config(sectorsNo, humidityArr, sensorsArr, sprinklersArr):
    data = {"sectors": []}

    for i in range(1, sectorsNo + 1):
        sectorObject = {
            "id": i,
            "sensor_id": sensorsArr[i - 1],
            "desired_humidity": humidityArr[i - 1],
            "sprinklers": sprinklersArr[i - 1]
        }

        data["sectors"].append(sectorObject)

    return data


def handle_weather_forecast(data):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="irrigation_system")
    location = geolocator.geocode(input("Podaj miasto dla którego ma zostać sprawdzona prognoza pogody: "))
    data["lat"] = location.latitude
    data["lon"] = location.longitude


if __name__ == '__main__':
    print("----SYSTEM NAWADNIAJĄCY TIR 2021/22----")

    mqttc = mosquitto.Mosquitto()
    mqttc_server = input("\nPodaj adres brokera MQTT: ")
    mqttc.connect(mqttc_server, 1883, 60)

    sensors = []
    sprinklers = []
    desiredHumidity = []

    numberOfSectors = int(input("\nPodaj liczbę sektorów do nawadniania: "))

    prepare_sensors(sensors, numberOfSectors)
    prepare_sprinklers(sprinklers, numberOfSectors)
    prepare_humidity_data(desiredHumidity, numberOfSectors)

    data = assemble_config(numberOfSectors, desiredHumidity, sensors, sprinklers)
    handle_weather_forecast(data)

    print(json.dumps(data))

    mqttc.publish("agh/iot/project9/config", json.dumps(data), retain=True)
