import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from datetime import datetime 
from prettytable import PrettyTable

prev_idList = []
prev_posList = []
def parsedisplay(self,params,packet):
	global prev_idList
	global prev_posList
	print(prev_posList)
	payloadMsg = json.loads(packet.payload)
	print("Received Message:", payloadMsg['timestamp'])
	#Process the ID list
	idList = list(eval(payloadMsg['occupantID']))

	posList = list(eval(payloadMsg['pos']))
	if len(idList)>1:
		idList, posList = zip(*sorted(zip(idList, posList)))
	table = [['Occupant ID', 'x (m)','dx', 'y (m)','dy','Event (x)','Event (y)']]
	tab = PrettyTable(table[0])
	
	for i in range(len(idList)):
		if i > len(prev_posList)-1: #New person has entered the room
			tab.add_row([idList[i],posList[i][0],'-',posList[i][1],'-','Entered','Entered'])
		else:
			currX = posList[i][0]
			prevX = prev_posList[i][0]
			currY = posList[i][1]
			prevY = prev_posList[i][1]
			dx,dy = round(currX-prevX,2),round(currY-prevY,2)

			#Action conditions for x 		
			print(dx,dy)
			if abs(dx) < 0.1:
				actionX = "Still"
			elif dx < 0:
				actionX = "Moving left"
			
			elif dx > 0:
				actionX = "Moving right"
			if abs(dy) < 0.15:
				actionY = "Still"
			
			#Action conditions for y
			elif dy < 0:
				actionY = "Moving towards"
			
			elif dy > 0:
				actionY = "Moving away"

			tab.add_row([idList[i],posList[i][0],dx,posList[i][1],dy,actionX,actionY])
	if len(idList) > 0:
		print(tab)
	if len(idList) < len(prev_idList):
		print("Person left the room")
	prev_posList = posList

myMQTTClient = AWSIoTMQTTClient("MacOS") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("a2rhn7hbr9ksxp-ats.iot.us-east-1.amazonaws.com", 8883)

myMQTTClient.configureCredentials("/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/AmazonRootCA1.pem", "/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/private_mac.pem.key", "/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/certificate_mac.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec
print ('Initiating Realtime Data Transfer From Raspberry Pi...')
myMQTTClient.connect()
myMQTTClient.subscribe("MLX90640", 1, parsedisplay)

while True:



	time.sleep(5)