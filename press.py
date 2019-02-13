#from gpiozero import Buzzer
import RPi.GPIO as GPIO
import time
import socket
import threading

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port=4971
connect=True
s.connect(('192.168.0.10',port))
clientRunning=True

Button1=10 #empty parking lot
LED=16 #LED
line_button=8 #warning system
warningsign=7 #piezo buzzer
flap=32 #flap->survo motor
trig=11 #sensor
echo=12 #sensor
tollbar= 15 # tollbar

empty={'1':'Button1','2':'Button2','3':'Button3'} #empty parking lot list

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


GPIO.setup(warningsign,GPIO.OUT)
GPIO.setup(Button1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(line_button,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED,GPIO.OUT)
GPIO.setup(flap,GPIO.OUT)
GPIO.setup(tollbar,GPIO.OUT)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo,GPIO.IN)


p1=GPIO.PWM(flap,50)
p2=GPIO.PWM(tollbar,50)
button_press=GPIO.input(Button1)



#pressure detect     #presscount%2==0 in&out     #presscount%2==1 in 

def press(s):
    presscount=0
    while True:
        count=0
        GPIO.output(LED,True)
        if GPIO.input(Button1)==GPIO.HIGH:
            presscount+=1
            print('ready for parking')
            time.sleep(1)
            while GPIO.input(Button1)==GPIO.LOW:
                GPIO.output(LED,False) #turn off LED
                if presscount%2==1:
                    count+=1
                    time.sleep(1)
                    print(count)
                    if count>=5:
                        print("no.1 is full")
                        
                        
                      #activate flap

                        
                        p1.start(12.5)
                        p1.ChangeDutyCycle(7.5)
                        time.sleep(1)
                        #p1.ChangeDutyCycle(7.5)
                        msg = '1'
                        if msg=='1':
                            s.send(bytes(msg,'utf-8'))
                        #count=0
                        #presscount=0
                       

                        break
                    
                else:
                    break
'''
def press(s): 
    presscount=0
    while True:
         count=0
         GPIO.output(LED, True)
         if GPIO.input(Button1)==GPIO.HIGH: #button pressed
            print("ready for parking")
            presscount+=1
            time.sleep(1)
            while GPIO.input(Button1)==GPIO.LOW: #After button pressed
                   if presscount%2==1:
                       count+=1
                       time.sleep(1)
                       print(count)
                       if count>=3 : #button pressed--->not pressed----->10sec----->parked
                           print("no.1 is full")
                           del empty['1'] #delete from empty parking lot list
                           GPIO.output(LED,False) #turn off LED
                           p1.start(7.5)
                           p1.ChangeDutyCycle(7.5)  #activate flap
                           time.sleep(1)
                           p1.ChangeDutyCycle(12.5)
                           msg = '1'
                           s.send(bytes(msg,'utf-8'))
                           presscount=0 
                           break
                           
                        #if button1 interrupt,count again from 0
                   else:
                       break
            #if money paid sign income-> p.start(12.5) /p.ChangeDutyCycle(12.5)/p.ChangeDutyCycle(7.5)
            #empty[i]='button i'
'''                 
def warning():
    while True:
        if GPIO.input(line_button)==GPIO.HIGH:#if button pressed
            print(" buzzer activate")
            while GPIO.input(line_button)==GPIO.HIGH: #while button pressed activate buzzer
                GPIO.output(warningsign,0)
                time.sleep(.2) 
                GPIO.output(warningsign,1)
                time.sleep(.2)

def Entrance():
    while True:
        count=0
        #caculate distance
        GPIO.output(trig,False)
        time.sleep(0.5)

        GPIO.output(trig,True)
        time.sleep(0.00001)
        GPIO.output(trig,False)

        while GPIO.input(echo)==0:
            pulse_start=time.time()

        while GPIO.input(echo)==1:
            pulse_end=time.time()

        pulse_duration= pulse_end - pulse_start
        distance=pulse_duration *17000
        distance=round(distance,2)
   
        
        # if distance<10 activate survo motor (toll bar)
        if int(distance)<10:
             p2.start(7.5)
          #activate flap
             
             p2.ChangeDutyCycle(12.5)
             for i in range(5):
                 
                 time.sleep(1)
                 
             p2.ChangeDutyCycle(7.5)


def reset(s):
    msg = 0
    while clientRunning:
        msg=s.recv(1024)
        msg = str(msg,'utf-8')
        print(msg)
        if msg=='1': #msg recv
            GPIO.output(LED,True) #turn on LED
             
            p1.start(7.5) # flap reset
            p1.ChangeDutyCycle(12.5)
            
            
         #if money paid sign income-> p.start(12.5) /p.ChangeDutyCycle(12.5)/p.ChangeDutyCycle(7.5)
            #empty[i]='button i'
        ###### cleanup nonreservation system
    

#press() warning() Entrance() reset(s)
def main():
    threading.Thread(target=reset, args=(s,)).start()
    threading.Thread(target=press,args=(s,)).start()
    threading.Thread(target=warning).start()
    threading.Thread(target=Entrance).start()        

main()
