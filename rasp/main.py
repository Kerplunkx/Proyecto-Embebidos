import paho.mqtt.client as mqtt
import time
import requests

TOKEN = "BBFF-sn9mPfimXLVpxvbeeacylABVZYwxFV"
DEVICE_LABEL = "raspi"
VARIABLE_LABEL_1 = "Producto"
VARIABLE_LABEL_2 = "Caducidad"

dic2={"0014B":{"vencimiento":"2022-08-28","alerta":"2022-08-21","creacion":"2022-08-21","post":0}}

productos = {"0001A": "Leche", "0002B": "Queso", "0003C": "Carne", "0004D": "Camarón"}

def build_payload(variable_1, variable_2, producto, sec_caducidad, alerta, creacion):
  for cod in dic2:
    if dic2[cod]["post"] == 1:
      payload = {variable_1: {"value":1,"context": {"Producto": producto, "vencimiento":time.strftime("%Y-%m-%d",time.localtime(sec_caducidad)), "alerta":alerta ,"creacion":creacion}},
               variable_2: 1}
    else: payload = {variable_1:0,
               variable_2: 0}
  return payload

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True

def main(producto, sec_caducidad, alerta, creacion):
  for cod in dic2:
    if time.strftime("%Y-%m-%d",time.localtime(time.time()))== dic2[cod]["alerta"]:
      dic2[cod]["post"]=1

  payload = build_payload(VARIABLE_LABEL_1, VARIABLE_LABEL_2, producto, sec_caducidad, alerta, creacion)
  print("[INFO] Attemping to send data")
  post_request(payload)
  print("[INFO] finished")

  for cod in dic2:
    if time.strftime("%Y-%m-%d",time.localtime(time.time()))== dic2[cod]["alerta"]:
      dic2[cod]["post"]=0

def on_connect(client, userdata, flags, rc):
    print("Conectado")
    client.subscribe("data")

def on_message(client, userdata, msg):
    data = msg.payload.decode("utf-8").split(",")
    producto = productos[data[0][data[0].index(" ") + 1: ]]
    dia = data[1][data[1].index(" ") + 1: ]
    mes = data[2][data[2].index(" ") + 1: ]
    año = data[3][data[3].index(" ") + 1: ]
    fecha = año + '-' + mes + '-' + dia
    sec_caducidad = time.mktime(time.strptime(fecha, "%Y-%m-%d"))
    alerta = time.strftime("%Y-%m-%d", time.localtime(sec_caducidad-604800))
    creacion = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    dic2.update({producto:{"vencimiento":fecha,"alerta":alerta,"creacion":creacion,"post":0}})
    main(producto, sec_caducidad, alerta, creacion)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

while True:
    client.loop()
