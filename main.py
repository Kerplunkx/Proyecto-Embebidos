import network
from machine import Pin, SoftI2C
from lcd.i2c_lcd import I2cLcd
from time import sleep
from umqtt.simple import MQTTClient

I2C_ADDR = 0x27
WIDTH  = 128                                          
HEIGHT = 64                                           
KEY_UP   = 0
KEY_DOWN = 1

SERVER = '192.168.100.68'
CLIENT_ID = 'ESP32_USER_INPUT'
TOPIC = b'data'

RED_CASA = 'NETWORK'
PASS_CASA = 'PASSWORD'

totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

keys = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]
cols = [19,13,15,23]
rows = [2,4,5,18]
row_pins = [Pin(pin_name, mode=Pin.OUT) for pin_name in rows]
col_pins = [Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in cols]
keypad_is_active = True

station = network.WLAN(network.STA_IF)
station.active(True)

if not station.isconnected():
    lcd.putstr("Conectando...")
    station.connect(RED_CASA, PASS_CASA)
    while not station.isconnected():
        pass
    lcd.clear()
    lcd.putstr("Conectado")
    sleep(2)
    lcd.clear()

client = MQTTClient(CLIENT_ID, SERVER, keepalive=60)
client.connect()

def init():
    for row in range(0,4):
        for col in range(0,4):
            row_pins[row].value(0)

def scan(row, col):
    """ scan the keypad """

    row_pins[row].value(1)
    key = None

    if col_pins[col].value() == KEY_DOWN:
        key = KEY_DOWN
    if col_pins[col].value() == KEY_UP:
        key = KEY_UP
    row_pins[row].value(0)

    return key

def get_keys(keypad_is_active, user_input):
    while keypad_is_active:
        for row in range(4):
            for col in range(4):
                key = scan(row, col)
                if key == KEY_DOWN:
                    last_key_press = keys[row][col]
                    user_input += last_key_press
                    print(user_input)
                    sleep(0.25)
                    if last_key_press == "*":
                        keypad_is_active = False
    return user_input

init()

while True:
    product = ""
    day = ""
    month = ""
    year = ""
    lcd.putstr("Producto:")
    sleep(2)
    lcd.clear()
    product = get_keys(True, product).strip("*")
    lcd.putstr(product)
    sleep(2)
    lcd.clear()

    lcd.putstr("Expiracion")
    sleep(2)
    lcd.clear()

    lcd.putstr("Dia:")
    sleep(2)
    lcd.clear()
    day = get_keys(True, day).strip("*")
    lcd.putstr(day)
    sleep(2)
    lcd.clear()

    lcd.putstr("Mes:")
    sleep(2)
    lcd.clear()
    month = get_keys(True, month).strip("*")
    lcd.putstr(month)
    sleep(2)
    lcd.clear()

    lcd.putstr("A" + chr(0xEE) + "o:")
    sleep(2)
    lcd.clear()
    year = get_keys(True, year).strip("*")
    lcd.putstr(year)
    sleep(2)
    lcd.clear()

    try:
        msg = f'Producto: {product},Dia: {day},Mes: {month},Año: {year}'
        client.publish(TOPIC, msg.encode())
    except OSError:
        print("Failed to read data")
