import board
from adafruit_bme280 import basic as adafruit_bme280
import time
i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
start_time = time.time()
while True:
    if time.time()-start_time > 1:
        print("\nTemperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.humidity)
        print("Pressure: %0.1f hPa" % bme280.pressure)
        start_time = time.time()
