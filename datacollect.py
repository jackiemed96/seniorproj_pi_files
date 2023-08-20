import socket, time
import Adafruit_DHT
import RPi.GPIO as GPIO

#Humidity/Temperature sensor
dhtSensor = Adafruit_DHT.DHT22
dhtPin = 17

#Ultrasonic Sensor
GPIO.setmode(GPIO.BCM)

trigPin = 27
echoPin = 22

GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

#Server Info
bufferSize = 1024

serverIP = "192.168.0.90"
serverPort = 2223

RPIserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RPIserver.bind((serverIP, serverPort))

print("Server up and listening . . .")

try:
    while (True):
        cmd, address = RPIserver.recvfrom(bufferSize)
        cmd = cmd.decode("utf-8")
        print(cmd)
        
        if (cmd == "GO"):
            #US Data Collection
            GPIO.output(trigPin, 0)
            time.sleep(2E-6)
            GPIO.output(trigPin, 1)
            time.sleep(10E-6)
            GPIO.output(trigPin, 0)

            while (GPIO.input(echoPin) == 0):
                pass
        
            echoStartTime = time.time()
        
            while (GPIO.input(echoPin) == 1):
                pass
        
            echoStopTime = time.time()
        
            ptt = echoStopTime - echoStartTime #ptt = ping travel time
        
            distance = 767 * ptt * ((5280 * 12)/3600)
            dtt = distance / 2 #dtt = distance to target
            dtt = round(dtt, 4)
            
            #Temp/Humidity Data Collection
            humidity, temp = Adafruit_DHT.read_retry(dhtSensor, dhtPin)
            temp = round(temp, 5)
            humidity = round(humidity, 5)
            
            #Sending Data
            data = str(temp) + ':' + str(humidity) + ':' + str(dtt)
            data = data.encode("utf-8")
            RPIserver.sendto(data, address)
        else:
            data = "Invalid Request"
            data = data.encode("utf-8")
            RPIserver.sendto(data, address)
            
        time.sleep(5)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program Exited")
