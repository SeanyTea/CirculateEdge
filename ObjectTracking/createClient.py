from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def createMQTTClient(clientID,endPoint,credentials):
    myMQTTClient = AWSIoTMQTTClient(clientID)
    #myMQTTClient.configureEndpoint("a2rhn7hbr9ksxp-ats.iot.us-east-1.amazonaws.com", 8883) #Provide your AWS IoT Core endpoint (Example: "abcdef12345-ats.iot.us-east-1.amazonaws.com")
    myMQTTClient.configureEndpoint("a2rhn7hbr9ksxp-ats.iot.us-east-1.amazonaws.com", 8883) #Provide your AWS IoT Core endpoint (Example: "abcdef12345-ats.iot.us-east-1.amazonaws.com")
    

    myMQTTClient.configureCredentials(credentials[0], credentials[1], credentials[2]) #Set path for Root CA and provisioning claim credentials
    myMQTTClient.configureOfflinePublishQueueing(-1)
    myMQTTClient.configureDrainingFrequency(2)
    myMQTTClient.configureConnectDisconnectTimeout(10)
    myMQTTClient.configureMQTTOperationTimeout(5)
    
    return myMQTTClient

