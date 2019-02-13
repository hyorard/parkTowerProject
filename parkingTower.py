#parktower.py
import socket
import sys
import threading
import RPi.GPIO as GPIO
import time



class parkTower:
    isSendID = False
    sortmark = "@"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
    
    def __init__(self,address):
        self.sock.connect((address,4969))
        self.run()


    def run(self):
        pin = 12
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin,GPIO.OUT)
        p = GPIO.PWM(pin,50)
        p.start(7.5)
        
        sthread  = threading.Thread(target = self.serverHandler)
        sthread.daemon = True
        sthread.start()


        while True:
            if self.isSendID == False:
                self.sendID()

            try:
                serverMsg = self.sock.recv(1024)
            except:
                break;

            serverMsg = str(serverMsg) 
            serverMsg = serverMsg.split(self.sortmark)
            svheader = serverMsg[0]

            if svheader == "ACode":
                ispass = serverMsg[1]
                parkinglot = serverMsg[2]

                if ispass == "True":
                    p.start(12.5)
                    time.sleep(1)
                    p.ChangeDutyCycle(7.5)
                    time.sleep(1)

                    p.ChangeDutyCycle(12.5)
                    time.sleep(1)

                    #ROATATER CODE
                    print(parkinglot+'parking slot')


                    
                elif ispass == 'False':
                    print('input False')######
                    
                else:
                    #LCD PRINT
                    print('lcd')########

    def sendID(self):
        ID = "parkTower"
        ID = bytes(ID)
        self.sock.send(ID)
        self.isSendID = True
        print("ID sent")


################################################################
    def serverHandler(self):
        msgHeader ="checkACode"
        certifi = ''

        #KEY GPIO SETTING
        GPIO.setmode(GPIO.BOARD)
        
        MATRIX = [
            ['1','2','3','A'],
            ['4','5','6','B'],
            ['7','8','9','C'],
            ['*','0','#','D']
            ]
        ROW =[31,33,35,37]
        COL =[32,36,38,40]

        GPIO.setwarnings(False)
        for j in range(4):
            GPIO.setup(COL[j],GPIO.OUT)
            GPIO.output(COL[j],1)

        GPIO.setwarnings(False)
        for i in range(4):
            GPIO.setup(ROW[i],GPIO.IN,pull_up_down = GPIO.PUD_UP)

        print('please your certification number')

        #USER INPUT & SEND TO SERVER
        try:
            while(True):
                for j in range(4):
                    GPIO.output(COL[j],0)
            
                    for i in range(4):
                        if GPIO.input(ROW[i]) == 0:
                            certifi = certifi + (MATRIX[i][j])
                            print('input',certifi)
                            #PRINT LCD
                            # - - -
                        
                            if len(certifi) >= 4:
                                towermsg = msgHeader + self.sortmark + certifi
                                self.sock.send(bytes(towermsg))
                                print('sent---',towermsg)
                                certifi = ''

                            while(GPIO.input(ROW[i]) == 0):
                                pass

                    GPIO.output(COL[j],1)
       
        except KeyboardInterrupt:
            GPIO.cleanup()

a = parkTower(sys.argv[1])
