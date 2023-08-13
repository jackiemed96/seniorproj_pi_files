import RPi.GPIO as GPIO
import time
import socket

bufferSize = 1024

serverIP = "192.168.0.90"
serverPort = 2222

RPIserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RPIserver.bind((serverIP, serverPort))

GPIO.setmode(GPIO.BCM)

trigPin = 27
echoPin = 22

GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

print("Server up and listening . . .")

try:
    while (True):
        cmd, address = RPIserver.recvfrom(bufferSize)
        cmd = cmd.decode("utf-8")
        print(cmd)
        
        if (cmd == "GO"): 
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
            
            dtt = str(dtt)
            dtt = dtt.encode("utf-8") 
            RPIserver.sendto(dtt, address)
        
            time.sleep(1)
    
except KeyboardInterrupt:
    GPIO.cleanup()
    print("GPIO Clean")
