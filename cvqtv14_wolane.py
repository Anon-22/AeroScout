from PyQt4 import QtCore, QtGui, uic
import sys
##import cv2
import numpy as np
import threading
import time
import queue
import design
import pyqtgraph as pg
import matplotlib
matplotlib.use('Qt4Agg')
import pandas as pd
import serial # import Serial Library
import numpy  # Import numpy 
import matplotlib.pyplot as plt #import matplotlib library 
from drawnow import *
import datetime
import pyautogui
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2 as cv
import os
#from moviepy.editor import VideoFileClip
import math
import sys
import random
import csv
from sys import argv
from imageai.Detection import ObjectDetection
import socket
import struct
import time

# Here we define the UDP IP address as well as the port number that we have 
# already defined in the client python script.
UDP_IP_ADDRESS = "192.168.0.13"
UDP_PORT_NO = 6789
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# One difference is that we will have to bind our declared IP address
        # and port number to our newly declared serverSock
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))



cogval_li=[]
tempC = []     #Empty array 
humidity = []
heat=[]
count = 0
temp=0
cogval_ret=0
counter=0
hum=0
heatind=0
arduino = serial.Serial('com5',115200)   #Serial port to which arduino is connected and Baudrate
plt.ion() #Tell matplotlib you want interactive mode to plot live data
running = False
capture_thread = None
#form_class = uic.loadUiType("simple.ui")[0]
q = queue.Queue()
prev = 0

###Camera Property
focus = 0




execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath( os.path.join(execution_path , "yolo.h5"))
detector.loadModel(detection_speed="normal")
 
    






def grab(cam, queue, width, height, fps):
    global running
    capture = cv.VideoCapture(cam)
    capture.set(cv.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv.CAP_PROP_FPS, fps)

    while(running):
        frame = {}        
        capture.grab()
        retval, img = capture.retrieve(0)
        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            #print (queue.qsize())
            pass

class OwnImageWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()



class MyWindowClass(QtGui.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        

        #self.startButton.clicked.connect(self.start_clicked)
        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)       
        global running
        running = True
        capture_thread.start()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

##        self.threadclassc=ThreadClassc()
##        self.threadclassc.start()
        
        self.threadclassb=ThreadClassb()
        self.threadclassb.start()

        width, height = pyautogui.size()
##        print(width,height)
        w = self.groupBox.width()
        h= self.groupBox_2.height()
        print(h)
##        print("Width",w1)
##        conLbl = QLabel("Continuous Plot",self)
##        conLbl.move(10,100)
        ##Temperature plot
        self.continuousPlt = pg.PlotWidget(self)
        self.continuousPlt.move(w+20,30)
        

        self.continuousPlt.setLabel('left', 'Temp', units='Degree C')
        self.continuousPlt.setLabel('bottom', 'Time', units='Sec')
        self.continuousPlt.setTitle('Temperature Graph', **{'color': '#FFF', 'size': '14pt'})
        pltT_w=width-(w+20)
        pltT_h=200 
        
        self.continuousPlt.resize(pltT_w,250)

        self.timer3 = pg.QtCore.QTimer()
        self.timer3.timeout.connect(self.cUpdate)
        self.timer3.start(1000)



        #Humidity Plot
        self.continuousPlt1 = pg.PlotWidget(self)
##        pltH_h=pltT_h+30+20
        pltH_h=290
        self.continuousPlt1.move(w+20,pltH_h)
        self.continuousPlt1.resize(pltT_w,250)

        self.continuousPlt1.setLabel('left', 'Humidity', units='g/m^3')
        self.continuousPlt1.setLabel('bottom', 'Time', units='Sec')
        self.continuousPlt1.setTitle('Humidity Graph', **{'color': '#FFF', 'size': '14pt'})
        self.timer2 = pg.QtCore.QTimer()
        self.timer2.timeout.connect(self.update)
        self.timer2.start(1000)


        #cogLoad Plot
        self.continuousPlt2 = pg.PlotWidget(self)
##        pltC_h=h-200
        pltC_h=550
        self.continuousPlt2.move(w+20,pltC_h)
        self.continuousPlt2.resize(pltT_w,250)

        self.continuousPlt2.setLabel('left', 'magnitude of Heat Index', units='g/m^3')
        self.continuousPlt2.setLabel('bottom', 'Time', units='Sec')
        self.continuousPlt2.setTitle('Heat Index Graph', **{'color': '#FFF', 'size': '14pt'})
        self.timer4 = pg.QtCore.QTimer()
        self.timer4.timeout.connect(self.update)
        self.timer4.start(1000)


        self.show()

    
    def cUpdate(self):
        global temp, counter, hum, prev,cogval_ret,heatind
       
       
##        now = datetime.datetime.now()
##        s = np.array([now.second])
##        print(s)
##        print(type(s))
        
##        temp=temp+1;
        counter=counter+1
        x=counter
##        y=x*5 # Test case for temp graph
##        y1=x*10 #Test case for humidity graph
        x = np.array([x])
##        tmpC=np.array([tempC])
       
        
        y = np.array([temp]) # temperature update
##        y = np.array([y])
        if (temp>35):
            self.continuousPlt.plot(x,y, pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        else:
            self.continuousPlt.plot(x,y, pen=(200,200,200), symbolBrush=(255,255,255), symbolPen='w')        
        #Optional plotting style
##        self.continuousPlt.plot(x, y, pen='b', symbol='x', symbolPen='b', symbolBrush=0.2, name='red')
        y1=np.array([hum])
##        y1 = np.array([y1])
##        self.continuousPlt1.plot(x,cog_val, pen=(200,200,200), symbolBrush=(0,0,255), symbolPen='w')
        if(hum>60):
            self.continuousPlt1.plot(x,y1, pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        else:
            self.continuousPlt1.plot(x,y1, pen=(200,200,200), symbolBrush=(255,255,255), symbolPen='w')


        y2=np.array([heatind])
        if (heatind>30):
            self.continuousPlt2.plot(x,y2, pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        else:
            self.continuousPlt2.plot(x,y2, pen=(200,200,200), symbolBrush=(0,255,0), symbolPen='w')

    def update_frame(self):
        if not q.empty():
            #self.startButton.setText('Camera is live')
            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1
            
            img = cv.resize(img, None, fx=scale, fy=scale, interpolation = cv.INTER_CUBIC)
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
##            img= process_image(img)
            img, detections = detector.detectObjectsFromImage(input_image=img, input_type="array", output_type="array", minimum_percentage_probability=30)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.ImgWidget.setImage(image)

    def closeEvent(self, event):
        global running
        running = False

        
class ThreadClassb(QtCore.QThread):
    def __init__(self):
        super(self.__class__, self).__init__()



    def run(self):
        global tempC, humidity,temp,hum,cogval_ret,heatind
        count = 0
        while True: # While loop that loops forever
            
            while (arduino.inWaiting()==0): #Wait here until there is data
                pass #do nothing
            
            arduinoString =arduino.readline() #read the data from serial port
            print('string:',arduinoString)
            #print(arduinoString)
            arduinoString = arduinoString.decode("utf-8")
        #dataArray = arduinoString.split(',')   #Split it into an array

            a=arduinoString.split(',') # a = temp
            b=a[1].split('\r\n') #b = hum
            c=a[2].split('\r\n')
            a=float(a[0])
            print('temp',a,type(a))     
            b=float(b[0])
            print('hum',b,type(b))
            c=float(c[0])
            
            
            temp = a
            hum = b
            heatind=c
       
            tempC.append(temp)                     #Build our tempC array by appending temp reading
            
            humidity.append(hum)                     #Building our humidity array by appending hum reading
            heat.append(heatind)
            
            count=count+1
            if(count>1):    #only take last 20 data if data is more it will pop first
                tempC.pop(0) # pop out first element
            
                humidity.pop(0)
                heat.pop(0)

capture_thread = threading.Thread(target=grab, args = (0, q, 1280, 760, 30))

app = QtGui.QApplication(sys.argv)
w = MyWindowClass(None)
w.setWindowTitle('WIRIN Dashboard')
w.show()
app.exec_()


