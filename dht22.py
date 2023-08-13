import socket
import time
import Adafruit_DHT

dhtSensor = Adafruit_DHT.DHT22
dhtPin = 17

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
            humidity, temp = Adafruit_DHT.read_retry(dhtSensor, dhtPin)
            
            if (humidity is not None and temp is not None):
                data = str(temp) + ':' + str(humidity)
                data = data.encode("utf-8")
                RPIserver.sendto(data, address)
            else:
                data = "Bad measurement"
                print(data)
                data = data.encode("utf-8")
                RPIserver.sendto(data, address)     
        else:
            data = "Invalid Request"
            data = data.encode("utf-8")
            RPIserver.sendto(data, address)
    # while (True):
    #     humidity, temp = Adafruit_DHT.read_retry(dhtSensor, dhtPin)
        
    #     if humidity is not None and temp is not None:
    #         print("Temp = {0:0.1f}*C Humidity = {1:0.1f}%".format(temp, humidity))
    #     else:
    #         print("Failed to retrieve data")
            
        time.sleep(5)
        
except KeyboardInterrupt:
    print("Program Exited")
