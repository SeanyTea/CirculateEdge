# CirculateIoT Documentation
This provides documentation for all of CirculateIoT, including the CirculateEdge device, AWS communication, and installation methods.

## Requirements and setup
### Required for CirculateEdge
* Raspberry Pi 4
* 32 GB SD card
* 64-bit Bullseye OS (Debian)

### Sensor requirements

* Intel RealSense D435 Depth Camera
* BME280 (Temperature + Humidity + Pressure)
* VEML7700 (Light)
* SGP30 (CO2)

### Local PC Setup

1. Download and install
[VNC viewer](https://www.realvnc.com/en/connect/download/viewer/)

### Raspberry Pi Setup

1. Install Debian Bullseye 64-bit on SD card using Raspberry Pi Imager

![Raspberry Pi Imager](MarkdownFiles/RPiImager.png)

2. Set-up Wi-Fi connection using monitor, mouse, and keyboard
    1. Click the settings button in the Raspberry Pi Imager
    
    2. Set hostname, enable SSH, set username and password, and enable WiFi connection

    ![Raspberry Pi Imager Settings](MarkdownFiles/RPIImagerSettings.png)

3. Insert SD card into Raspberry Pi and set-up headless resolution for remote
    1. SSH using the hostname and password previously set-up.

    2. Enter the command hostname -I in the terminal to find the Pi's IP address. Save for use with VNC viewer.

    3. Edit the config file using 

    ```
    sudo raspi-config
    ```

    and enable headless monitoring, VNC, and I2C.
    ![Main config](MarkdownFiles/main_config.png)
    ![Display Options](MarkdownFiles/display_options.png)
    ![Interface Options](MarkdownFIles/interface_options.png)
    Restart the Raspberry Pi for effects to take change.

4. On your local PC, insert the IP address found into VNC viewer.

## Installation

1. Install virtual environment

```
pip install virtualenv
```
and add the following line to add the virtualenv bin folder to the path:

```
nano ~/.bashrc
export PATH=$PATH:/home/pi/.local/bin
```
Relog for effects to take place. Create the virtual environment and activate:

```
virtualenv circulate
source circulate/bin/activate
```

2. Install Intel RealSense using the instructions following [Github Link](https://github.com/datasith/Ai_Demos_RPi/wiki/Raspberry-Pi-4-and-Intel-RealSense-D435). If OpenSSL can't be found, run 

```
sudo apt-get install libssl-dev
```

To install pyopengl-accelerate, use the following command: 
```
sudo pip3 install git+https://github.com/mcfletch/pyopengl.git@227f9c66976d9f5dadf62b9a97e6beaec84831ca#subdirectory=accelerate

```
3. Clone the CirculateEdge repository onto the local machine and install the required packages
```
git clone https://github.com/SeanyTea/CirculateEdge

cd CirculateEdge

pip install -r requirements.txt

```

## CRON for Job Automation

Cron is a command-line utility job scheduler on UNIX Operating Systems. Cron is used to schedule. To set-up cron:

1. Change the Time Zone settings using

``` 
sudo raspi-config
```
and select 'Localisation Options'

2. Using the terminal, set-up a crontab job

```
cron -e

```

Each task is defined through a single line. To setup a cron job at 9 am every day, use the following:
```
m h dom mon dow command
0 9 * * *  python3  /home/intelligentmedicine/Desktop/CirculateEdge/circulateEdge.py
```
Change the path accordingly.

A few useful commands:
1. To start cron:
```
sudo service cron start
```
2. To stop cron:
```
sudo service cron stop
```
3. To restart a cron job:
```
sudo service cron restart
```
4. To check active cron jobs and its PID (in brackets):
```
systemctl status cron
```
5. To kill a cron job:
```
kill [PID]
```

# AWS Iot Core + DynamoDB

## IoT Core Setup
1. Log-in to AWS IoT Core. Under 'Connect', click 'Connect one Device'. Each CirculateEdge device will be its own thing.

2. Enter Thing name and choose CirculateEdge as Thing type. Click Next.

![Thing Type](MarkdownFiles/create_thing.png)

3. Under Platforms/SDK, choose Linux/macOS and Python

4. Download the connection kit
![Connection Kit](MarkdownFIles/connectionKit.png)

5. Follow instructions and run the connection kit to test conenctivity.
![Test connection](MarkdownFiles/testConnection.png)

6. Move the certification to the appropriate folder, and change the PATH in CirculateEdge folder

## Python SDK for AWSIoT
We utilize the Python AWSIoTMQTTClient SDK to publish and subscribe to topics for each CirculateEdge device. Each sensor is associated with its own client and topic. To connect to a client, we use createClient.py, which takes in as inputs:

1. clientID : name of client. This can be arbitrary, but is specifically used to monitor lifetime cycle events.

2. endPoint : The AWS host endPoint. This is provided in 'Settings' under the AWS IoT Core navigation pane.
![Endpoint](MarkdownFiles/endPoint.png)

3. credentials: A list containing the path to the require credentials: RootCA, private key, and certificate.

For each sensor, a client is created, then connected. For example, the bmeClient is created as:

```
bmeClient = createMQTTClient('bmeSensor',endPoint,credentials)
bmeClient.connect()
```

## Publishing and Subscribing to a Topic
An MQTT client is any device (for example, a computer or a mobile phone) that connects to the broker. A client that sends messages is a publisher. A client that receives messages is a subscriber. To receive a message, the client must subscribe to the topic of that message. In our case, both the CirculateEdge device and AWS will act as the publisher/subscriber. 

In order to publish to a topic from the Python SDK, we must publish the data in JSON string format. Conventiently, we can store the data as a dictionary, and dump it as a JSON. An example can be found below:

```
bmeData = {}
bmeData['Temperature'] = bme280.temperature
bmeData['Humidty'] = bme.humidity
bmeData['Pressure'] = bme280.pressure
payloadMsg = json.dumps(bmeData)
bmeClient.publish(topic = "sensor/BME280", QoS = 1, payload = payloadMsg)
```
The structure of the topic name is important, but will be discussed later.

To subscribe to a topic, navigate to MQTT test client in AWS IoT Core and enter the topic name

![AWSIoT Subscribe](MarkdownFiles/awsSubscribe.png)

In order to save the data, we will route the message to AWS DynamoDB, Amazon's Fast NoSQL Key-Value Database. Under the navigation pane, go to Rules -> Message Routing and click 'Create Rule'. Enter a rule name and click next.
![Message Rule](MarkdownFiles/createRule.png)

Under the SQL statement, enter the following:

```
SELECT * FROM 'sensor/+'
```
This will select all attributes of the payload message from topics that begin with "sensor/". Click Next.

Attach the DynamoDBv2 rule action, which will split the payload message into multiple columns by attribute. Create a table, and enter 'GSIPK' (Global Secondary Index Partition Key) and 'GSISK' under the Partition Key, and Sort Keys respectively. This will allow us to partition and sort our table.

We utilize the [single-table design](https://aws.amazon.com/blogs/database/single-table-vs-multi-table-design-in-amazon-dynamodb/) following the [secondary index + query best practices](https://www.youtube.com/watch?v=BnDKD_Zv0og&ab_channel=AWSPortsmouthUserGroup).
Since we have multiple users, with multiple devices and sensors, we use the following table design:

| GSIPK | GSISK | Attribute 1 | Attribute 2 | Attribute 3 
| --------- |:---|:---------|:-----|:-----
| ORG#URBANCOWORKS#ROOM#OFFICE | SENSOR#BME280#TIMESTAMP | Temp. | Humidity | Pressure
| ORG#URBANCOWORKS#ROOM#HALLWAY | SENSOR#SGP30#TIMESTAMP | CO2 | TVOC |

Next, create a new IAM role (or select existing), and name it accordingly. Once the IAM role is created, click 'View' and add the AWSIoTRuleActions policy
![AWSIoTRuleActions](MarkdownFiles/IAMRulePolicy.png).

Now in the Python script, add the following GSIPK and GSISK for each sensor accordingly:

```
bmeData['GSIPK'] = 'ORG#URBANCOWORKS#ROOM#OFFICE'
bmeData['GSISK'] = 'SENSOR#BME280#' + str(time.time())
```
Now, when the payload message is published, it will automatically be routed to DynamoDB.







### NEED CUSTOM CLIENTS + TOPIC NAMES IN CODE!!

# Github
Personal acces token: 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
