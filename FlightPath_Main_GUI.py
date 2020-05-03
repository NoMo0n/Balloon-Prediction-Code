# Code by Daniel Constien

#General Code Credits:
#Balloon Class, File Extractor - Spencer Lankford
#UI - Daniel Constein
#Glider Class - AJ Burba


import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import math as mth

# Import functions from other files here
from flightpath_ui import Ui_Dialog
from FileExtractor import fileExtractor
from BalloonClass import balloon
from GliderClass import Glider

def flightPath(mywindow,balloonobj,Glider):
    #Plots the flight path for th balloon and glider

    mywindow.figure.clf()
    x = balloonobj.postX
    y = balloonobj.postY
    ax = mywindow.figure.add_subplot(111)
    ax.set_title('Ballon and Glider Flight Path')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.plot(x, y, 'r-')
    ax.plot(Glider.x,Glider.y, 'b-')
    ax.legend(['Balloon', 'Glider'], loc='upper left')
    mywindow.draw()

def plotXY(mywindow,balloonobj):
    #Plots the x and y position of the balloon over time

    mywindow.figure.clf()
    # x distance vs time
    x = balloonobj.postX
    t = balloonobj.timeTo
    # y distance vs time
    y = balloonobj.postY
    z = balloonobj.timeTo
    ax = mywindow.figure.add_subplot(221)
    ax.set_title('Balloon Flight X-Y')
    ax.set_xlabel('Time - s')
    ax.set_ylabel('X and Y - m')
    ax.plot(t, x, 'b-', z, y, 'r-')
    ax.legend(['X', 'Y'], loc='upper left')
    mywindow.draw()

def plotXYDot(mywindow,balloonobj):
    #Plots the x and y velocities of the balloon over time


    mywindow.figure.clf()
    # x velocity vs time
    x = balloonobj.postVX
    t = balloonobj.timeTo
    # y velocity vs time
    y = balloonobj.postVY
    z = balloonobj.timeTo
    ax = mywindow.figure.add_subplot(222)
    ax.set_title('Balloon Flight Xdot - Ydot')
    ax.set_xlabel('Time - s')
    ax.set_ylabel('Xdot and Ydot - m/s')
    ax.plot(t, x, 'b-', z, y, 'r')
    ax.legend(['Xdot', 'Ydot'], loc='upper left')
    mywindow.draw()

class PlotCanvas(FigureCanvas):
    def __init__(self,parent,width=None,height=None,dpi=100):
        if width == None: width = parent.width()/150
        if height == None: height = parent.height()/150
        fig = Figure(figsize=(width,height),dpi=dpi)
        FigureCanvas.__init__(self,fig)
        self.setParent(parent)

class main_window(QDialog):
    def __init__(self,):
        super(main_window,self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.assign_widgets()

        self.flight = PlotCanvas(self.ui.flightPath_2)
        self.xy = PlotCanvas(self.ui.flightXY)
        self.xydot = PlotCanvas(self.ui.flightXYdot)

        # Assigning a startup file
        self.filename = None
        self.startupname = "Balloon 3.txt"
        self.show()

    def assign_widgets(self):
        self.ui.exit.clicked.connect(self.ExitApp)
        self.ui.calculate.clicked.connect(self.Calculate)
        self.ui.openFile.clicked.connect(self.file)

    def file(self):
        #activates when file button is selected
        #pulls in new file data and precesses it for use

        try:
            self.startupname = QFileDialog.getOpenFileName()[0]
            self.filename = self.startupname
            self.ui.textEdit_fileName.setText("{}".format(self.startupname))

            f1 = open(self.filename, 'r')
            data = f1.readlines()
            myNet = fileExtractor()
            myNet.readFileData(data)
            f1.close()

            self.ui.comboBox_balloon.clear()
            self.ui.comboBox_wind.clear()
            self.ui.comboBox_glider.clear()
            self.ui.altitude.setText(None)
            self.ui.diameter.setText(None)
            self.ui.step.setText(None)
            self.ui.time.setText(None)
            self.ui.comboBox_balloon.addItems(myNet.balloonOptions)
            self.ui.comboBox_wind.addItems(myNet.windOptions)
            self.ui.comboBox_glider.addItems(myNet.gliderOptions)
            self.ui.altitude.setText("{}".format((myNet.simRequest[5])))
            self.ui.diameter.setText("{}".format((myNet.simRequest[1])))
            self.ui.step.setText("{}".format(myNet.simControl[1]))
            self.ui.time.setText("{}".format(myNet.simControl[0]))
            self.ui.mass.setText("{}".format(myNet.simRequest[4]))

            self.myReport(myNet)
        except:
            print("Incorrect File Type, Please Check the File Name or Integrity")

    def Calculate(self):
        #Pulls in user input data and processes the request

        try:
            if self.startupname != None:
                self.filename = self.startupname
            else:
                self.filename = QFileDialog.getOpenFileName()[0]

            f1 = open(self.filename, 'r')
            data = f1.readlines()
            myNet = fileExtractor()
            myNet.readFileData(data)
            f1.close()

            if self.ui.diameter.text() == '':
                #If the user input values are empty, update them with
                #information from the txt
                self.ui.comboBox_balloon.clear()
                self.ui.comboBox_wind.clear()
                self.ui.comboBox_glider.clear()
                self.ui.altitude.setText(None)
                self.ui.diameter.setText(None)
                self.ui.step.setText(None)
                self.ui.time.setText(None)
                self.ui.comboBox_balloon.addItems(myNet.balloonOptions)
                self.ui.comboBox_wind.addItems(myNet.windOptions)
                self.ui.comboBox_glider.addItems(myNet.gliderOptions)
                self.ui.altitude.setText("{}".format((myNet.simRequest[5])))
                self.ui.diameter.setText("{}".format((myNet.simRequest[1])))
                self.ui.step.setText("{}".format(myNet.simControl[1]))
                self.ui.time.setText("{}".format(myNet.simControl[0]))
                self.ui.mass.setText("{}".format(myNet.simRequest[4]))
            else:
                #If the input values are full, pull them and use them for the balloon and glider process
                myNet.simRequest[0] = self.ui.comboBox_balloon.currentText()
                myNet.simRequest[1] = float(self.ui.diameter.text())
                myNet.simRequest[2] = self.ui.comboBox_glider.currentText()
                myNet.simRequest[3] = self.ui.comboBox_wind.currentText()
                myNet.simRequest[4] = float(self.ui.mass.text())
                myNet.simRequest[5] = float(self.ui.altitude.text())
                myNet.simControl[0] = float(self.ui.time.text())
                myNet.simControl[1] = float(self.ui.step.text())
                myNet.readFileData(data)

            self.myReport(myNet)
        except:
            print("Incorrect Input Type, Please Check the Input Values and Try Again")

        return

    def myReport(self,myNet):
        #This is the heart of the UI's data processing capabilities.
        #All requests to BalloonClass and GliderClass go through here
        #this allows for a cleaner, less cluttered code.

        #Pass user data to balloon and process
        myBalloon = balloon(myNet, 0, 0, myNet.simRequest[4])
        myBalloon.myPath()

        #Pass user data and balloon data to glider and process
        myGlider = Glider(myNet)
        myGlider.ReturnHome(max(myBalloon.postY),max(myBalloon.postX),myNet.windDat,myNet.simRequest[4],myNet.simControl[0],myNet.simControl[1])

        # Formatting when data is passed into the report
        self.ui.balloonReport_2.setText('')

        # Constraints are printed in Balloon Report
        self.ui.balloonReport_2.append('                   StratoGlider Flight Performance')
        self.ui.balloonReport_2.append('\n Title: {}              '.format(myNet.title))
        self.ui.balloonReport_2.append('\n Launch Diameter: {}              '.format(self.ui.diameter.text()))
        self.ui.balloonReport_2.append('\n Payload Mass: {}              '.format(self.ui.mass.text()))
        self.ui.balloonReport_2.append('\n Wind Condition: {}              '.format(myNet.windOptions[0]))
        self.ui.balloonReport_2.append(
            '\n Glider Deployment Altitude: {}              '.format(self.ui.altitude.text()))
        self.ui.balloonReport_2.append('\n Glider Name: {}              '.format(myNet.gliderOptions[0]))
        self.ui.balloonReport_2.append('\n\n\n          Balloon at Deployment Altitude')
        self.ui.balloonReport_2.append(
            '\n Flight Time: {:.2f} seconds             '.format(myBalloon.finalTime))
        self.ui.balloonReport_2.append('\n Ground Distance Travelled: {:.2f} '.format(max(myBalloon.postX)))
        self.ui.balloonReport_2.append('\n Final Diameter: {:.2f} feet  '.format(myBalloon.saveR*2))
        self.ui.balloonReport_2.append('\n Burst Diameter: {:.2f} feet  '.format(myNet.balloonDat[3]))
        self.ui.balloonReport_2.append('\n\n\n          Glider Return Flight')
        self.ui.balloonReport_2.append('\n    Glider cannot return to launch site.')
        self.ui.balloonReport_2.append(
            '\n          It flies for {:.2f} seconds'.format(myGlider.maxTGlider))  # change the flight time
        self.ui.balloonReport_2.append('\n          It reaches the ground {:.2f} meters away from the launch site'.format((max(myGlider.x)-min(myGlider.x))))  # change the distance travelled

        #Request plots for the current simulation
        flightPath(self.flight,myBalloon,myGlider)
        plotXY(self.xy,myBalloon)
        plotXYDot(self.xydot,myBalloon)

    def ExitApp(self):
        app.exit()

def no_file():
    #If you are reading this have a great summer!
    msg = QMessageBox()
    msg.setText('There was no file selected')
    msg.setWindowTitle("No File")
    retval = msg.exec_()
    return None

def bad_file():
    msg = QMessageBox()
    msg.setText('Unable to process the selected file')
    msg.setWindowTitle("Bad File")
    retval = msg.exec_()
    return None

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()

    # If there is a file loaded on startup then run the main program
    if main_win.startupname is not None:
        main_win.Calculate()

    sys.exit(app.exec_())