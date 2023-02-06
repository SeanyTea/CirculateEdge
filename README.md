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




# Github
Personal acces token: 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
