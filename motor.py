import RPi.GPIO as GPIO
import time, board, socket

from adafruit_seesaw.seesaw import Seesaw

class PlanterStateMachine:
    def __init__(self):
        #Motor variables
        self.Motor1A = 5 #Pin 29 on Pi
        self.Motor1B = 6 #Pin 31 on Pi
        self.Motor1E = 16 #Pin 36 on Pi

        #Moisture sensor variables
        self.i2c_bus = board.I2C()  # uses board.SCL and board.SDA
        self.ss = Seesaw(self.i2c_bus, addr = 0x36)

        self.localAddress = ("127.0.0.1", 9999)
        self.bufferSize = 1024

        self.UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # initialize variables
        # moisture percentage = ((m_w - m_d) / m_d) * 100
        self.p_min = 0.3      # moisture percentage minimum (30% = 0.3)
        #self.p_max = 0.8      # moisture percentage maximum (80% = 0.8)
        self.p_max = 0.5      # moisture percentage maximum (50% = 0.5)
        self.m_w_min = None   # calculated minumum wet weight for dm
        self.m_w_max = None   # calculated maximum wet weight for dm
        self.base_w = 54.0    # base weight with no water 
        self.dm = None        # dm = m_w_max - m_w_min
        self.dt = None        # dt = dm / m
        self.v = 0.00000166   # 1.6e-6 m^3/sec; this is the volumetric flow rate of motor = 100ml/min converted to m^3/sec
        self.p = 1000         # density of water = 1000 kg/m^3
        self.m = self.v * self.p        # mass flow rate (kg/sec) = v * p
        
        self.m_w_base = self.base_w / 1000            # wet soil weight (g --> kg)
        
        # dimensions of water tank (m)
        self.height_tank = 0.2794 
        self.length = 0.12
        self.width = 0.04
        self.v_tank = self.height_tank * self.length * self.width
        
    # Checking water level to make sure there is enough water
    def checklevel(self):
        t1 = "localcommand"
        t1 = t1.encode("utf-8")
        self.UDPClient.sendto(t1, self.localAddress)
        waterlevel, address = self.UDPClient.recvfrom(self.bufferSize)
        waterlevel = waterlevel.decode("utf-8") #this is a string

        waterlevel = float(waterlevel)
        waterlevel_meters = waterlevel * 0.0254

        # calculations related to water dispensing
        v_wtd = 0.00000166 * self.dt                   # (m^3) volume of water to be dispensed for the certain amount of time
        h_wtd = 5 * (v_wtd / (self.width * self.length))    # height of water to be dispensed (m)
                                                  # this value is too small and not within the resolution of the ultrasonic sensor
                                                  # use 5x the value to give cushion before water runs out for user to refill tank
        h_min = self.height_tank - h_wtd               # (m) minimum height the water can be at before needing to refill

        # h_min:  0.256785831381733
        print("h_wtd: ", h_wtd)
        print("h_min: ", h_min)

        if (waterlevel_meters < h_min and waterlevel < 8.0):
            return True
        else:
            return False 
        
    def dontchecklevel(self):
        t1 = ""
        t1 = t1.encode("utf-8")
        self.UDPClient.sendto(t1, self.localAddress)

    def moisturesens(self):
        moisture = self.ss.moisture_read()
        print("Moisture: ", moisture)

        if (moisture < 370):
            return True
        else:
            return False

    def pump_calculations(self):
        soil_measure = self.ss.moisture_read()   # read from sensor for p_measure calculation 
        p_measure = soil_measure / 1800     # p_measure = (moisture_level / 1800); 1800 from soil sensor datasheet: values from 200 (very dry) to 2000 (very wet)
        m_d = (self.m_w_base / (p_measure + 1))  # dry soil weight - calculated from using soil moisture value (g --> kg)
                                            #     m_d = (m_w / (p_measure + 1))

        m_w_min = m_d * (self.p_min + 1)
        m_w_max = m_d * (self.p_max + 1)
        self.dm = m_w_max - m_w_min

        self.dt = self.dm / self.m
        print("time: ", self.dt)

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Motor1A, GPIO.OUT)
        GPIO.setup(self.Motor1B, GPIO.OUT)
        GPIO.setup(self.Motor1E, GPIO.OUT)
        
    def loop(self):
        #on
        GPIO.output(self.Motor1A, GPIO.HIGH)
        GPIO.output(self.Motor1B, GPIO.LOW)
        GPIO.output(self.Motor1E, GPIO.HIGH)
        print("Motor on")
        
        time.sleep(self.dt)
        
        #off
        GPIO.output(self.Motor1E, GPIO.LOW)
        GPIO.output(self.Motor1A, GPIO.LOW)
        print("Motor off")

    def run(self):
        #schedule.every(10).seconds.do(self.moisturesens)
        while True:
            time.sleep(10)
            needToWater = self.moisturesens()

            if (needToWater):
                can_water = self.checklevel()

                if (can_water):
                    self.loop()
                else:
                    print("Not Enough Water To Dispense")
                    continue

            else:
                self.dontchecklevel()
                continue

    def clean(self):
        GPIO.cleanup()
    
if __name__ == '__main__':

    plant = PlanterStateMachine()
    plant.setup()
    plant.pump_calculations()

    try: 
        plant.run()

    except KeyboardInterrupt:
        plant.clean()
        
        