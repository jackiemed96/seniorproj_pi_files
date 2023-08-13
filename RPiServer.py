import socket
import time

bufferSize = 1024
count = 0

msgFromServer = "Server says whats up dog?"

serverPort = 2222

serverIP = "192.168.0.91"

bytesToSend = msgFromServer.encode("utf-8")

RPIsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #creating socket
RPIsocket.bind((serverIP, serverPort)) #binding socket to server ip and port as a tuple

print("Server is up and listening . . . ")

while True: 
    message, address = RPIsocket.recvfrom(bufferSize)

    message = message.decode("utf-8")

    print(message)
    
    if (message == "INC"):
        count = count + 1
    
    if (message == "DEC"):
        count = count - 1

    msg = str(count)
    msg = msg.encode("utf-8")
    RPIsocket.sendto(msg, address)

