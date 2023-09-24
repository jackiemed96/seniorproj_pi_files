import RPi.GPIO as GPIO
import time, board, schedule, socket
import threading

from adafruit_seesaw.seesaw import Seesaw

#Motor variables
Motor1A = 5 #Pin 29 on Pi
Motor1B = 6 #Pin 31 on Pi
Motor1E = 4 #Pin 7 on Pi

#Moisture sensor variables
i2c_bus = board.I2C()  # uses board.SCL and board.SDA
ss = Seesaw(i2c_bus, addr = 0x36)

localAddress = ("127.0.0.1", 9999)
bufferSize = 1024

UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def checklevel():
    t1 = "localcommand"
    t1 = t1.encode("utf-8")
    UDPClient.sendto(t1, localAddress)
    waterlevel, address = UDPClient.recvfrom(bufferSize)
    waterlevel = waterlevel.decode("utf-8")

    print("Water level: ", waterlevel)

def dontchecklevel():
    t1 = ""
    t1 = t1.encode("utf-8")
    UDPClient.sendto(t1, localAddress)

def moisturesens():
    moisturedata = ss.moisture_read()
    print("Moisture: ", moisturedata)

    if (moisturedata < 400):
        x = threading.Thread(target=checklevel, args=())
        x.start()
    else:
        x = threading.Thread(target=dontchecklevel, args=())
        x.start()

    # if (moisturedata < 450):
    #     print("Meow!")
    
    # if (data < 400):
    #     loop()

#schedule moisture sensor to take data every x time
schedule.every(3).seconds.do(moisturesens)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Motor1A, GPIO.OUT)
    GPIO.setup(Motor1B, GPIO.OUT)
    GPIO.setup(Motor1E, GPIO.OUT)
    
def loop():
    #on
    GPIO.output(Motor1A, GPIO.HIGH)
    GPIO.output(Motor1B, GPIO.LOW)
    GPIO.output(Motor1E, GPIO.HIGH)
    print("Motor on")
    
    time.sleep(5)
    
    #off
    GPIO.output(Motor1E, GPIO.LOW)
    GPIO.output(Motor1A, GPIO.LOW)
    print("Motor off")
    
def clean():
    GPIO.cleanup()
    
if __name__ == '__main__':

    setup()

    try: 
        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        clean()
        
        