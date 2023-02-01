# Initialize I2C addresses
import board
import board
import busio
import adafruit_mlx90640
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_sgp30
from sgp30 import SGP30
import adafruit_veml7700
import sys
from createClient import createMQTTClient
import json
import time

#Define path to certificates
PATH_TO_CERT = '/home/intelligentmedicine/Desktop/CirculateEdge_000_Certificates/'
credentials = [PATH_TO_CERT + 'AmazonRootCA1.pem',PATH_TO_CERT+'private_circulateEdge000.pem.key', PATH_TO_CERT + 'certificate_circulateEdge000.pem.crt']
endPoint = 'a2rhn7hbr9ksxp-ats.iot.us-east-1.amazonaws.com'

#Setup devices
#	-BME280 is located at 0x77
#	-SGP30 is located at 0x58
#	- VEML7700 is located at 0x10
#	- MLX90640 is locateed at 0x33
i2c = board.I2C()  # uses board.SCL and board.SDA
prevAddresses = [hex(device_addresses) for device_addresses in i2c.scan()]
print(prevAddresses)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c) # Temp + pressure sensor
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
print("Sensor warming up, please wait...")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

#sgp30.start_measurement(crude_progress_bar)
#sys.stdout.write('\n')
#mlx = adafruit_mlx90640.MLX90640(i2c)
#veml7700 = adafruit_veml7700.VEML7700(i2c)

    
# result = sgp30.command('set_baseline', (0xFECA, 0xBEBA))
# result = sgp30.command('get_baseline')
# print(["{:02x}".format(n) for n in result])
'''
print("Sensor warming up, please wait...")
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')
'''

#Create clients for each device
bmeClient = createMQTTClient('bmeSensor',endPoint,credentials)
bmeClient.connect()

sgpClient = createMQTTClient('sgpSensor',endPoint,credentials)
sgpClient.connect()

mlxClient = createMQTTClient('mlxSensor',endPoint,credentials)
mlxClient.connect()

vemlClient = createMQTTClient('vemlSensor',endPoint,credentials)
vemlClient.connect()

deviceClient = createMQTTClient('deveiceHealth',endPoint,credentials)
deviceClient.connect()

testClient = createMQTTClient('test',endPoint,credentials)
testClient.connect()

# Useful functions
def handleConnections(currentAddresses,prevAddresses):
	for address in (set(prevAddresses) - set(currentAddresses)):
		if address == '0x33':
			print("MLX90640 has been disconnected")
			mlxClient.disconnect();
		elif address == '0x77':
			print("BME280 has been disconnected")
			bmeClient.disconnect();
		elif address == '0x10':
			print("VEML7700 has been disconnected")
			vemlClient.disconnect();
		elif address == '0x58':
			print("SGP30 has been disconnected")
			sgpClient.disconnect();
		
	for address in (set(currentAddresses) - set(prevAddresses)):
		if address == '0x33':
			print("MLX90640 has been disconnected")
			mlxClient.disconnect();
		elif address == '0x77':
			print("BME280 has been connected")
			bmeClient.connect();
		elif address == '0x10':
			print("VEML7700 has been connected")
			vemlClient.connect();
		elif address == '0x58':
			print("SGP30 has been connected")
			sgpClient.connect();
def monitorHealth(currentAddresses):
    currentHealth = {
        'MLX90640' : 'offline',
        'BME280' : 'offline',
        'SGP30' : 'offline',
        'VEML7700' : 'offline'
        }
    for address in currentAddresses:
        if address == '0x33':
            currentHealth['MLX90640'] = 'online'
        elif address == '0x77':
            currentHealth['BME280'] = 'online'
        elif address == '0x10':
            currentHealth['VEML7700'] = 'online'
        elif address == '0x58':
            currentHealth['SGP30'] = 'online'
    print(currentHealth)
    payloadMsg = json.dumps(currentHealth)
    deviceClient.publish('DeviceHealth', QoS = 1, payload = payloadMsg)
currentTime = time.time()
def helloworld(self,params,packet):
	print("Received Message")
	print("Payload:",packet.payload)
	
cnt = 0
while True:
    #First handle device connectivity
    currentAddresses = [hex(device_addresses) for device_addresses in i2c.scan()]
    monitorHealth(currentAddresses)
    '''
    if (time.time() - currentTime) > 10:
        monitorHealth(currentAddresses)
        currentTime = time.time()
    '''
    #handleConnections(currentAddresses, prevAddresses)
    prevAddresses = currentAddresses
    currentTime = time.time()
    bmeData = {}
    sgpData = {}
    bmeData['deviceID'] = "1"
    bmeData['timestamp'] = str(currentTime)
    bmeData['Temperature'] = round(bme280.temperature,2)
    bmeData['Humidity'] = round(bme280.humidity,2)
    payloadMsg = json.dumps(bmeData)
    
    bmeClient.publish(topic = "BME280", QoS=1, payload = payloadMsg)
    #result = sgp30.get_air_quality()
    
    sgpData['deviceID'] = "2"
    sgpData['timestamp'] = str(currentTime)
    sgpData['CO2'] = sgp30.eCO2
    sgpData['TVOC'] = sgp30.TVOC
    print(sgpData)
    payloadMsg = json.dumps(sgpData)
    sgpClient.publish(topic = "SGP30", QoS = 1, payload = payloadMsg)
    cnt+=1
    time.sleep(1)
