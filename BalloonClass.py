# Code by Spencer Lankford

import math as mth

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from scipy.integrate import odeint

from FileExtractor import fileExtractor


class balloon:
    def __init__(self, myFile ,initialX=0, initialY=0, initialAlt=0):
        # Initialization Step
        self.ID = myFile.balloonDat[0]
        self.balloonM = myFile.balloonDat[1]
        self.minR = float(myFile.balloonDat[1])
        self.startR = float(myFile.simRequest[1])
        self.maxR = myFile.balloonDat[3]
        self.CDo = myFile.gliderDat[4]
        self.payloadM = myFile.gliderDat[3]
        self.additionalPayload = myFile.simRequest[4]
        self.maxTime = myFile.simControl[0]
        self.nsteps = myFile.simControl[1]
        self.windDat = myFile.windDat
        self.initX = initialX
        self.initY = initialY
        self.initAlt = initialAlt
        self.finalAlt = myFile.simRequest[5]
        self.hMass = 0
        self.postX = []
        self.postY = []
        self.postVX = []
        self.postVY = []
        self.timeAccume = []
        self.timeTo = None
        self.finalTime = 0
        self.saveR = 0
        self.save = False


    def myCD(self, Re):
        # Initialize phi variables
        # NOTE: This equation was found in the research
        # paper provided on canvas
        if Re < .01:
            return 100
        else:
            phi1 = ((24 * Re ** -1) ** 10) + ((21 * Re ** -.67) ** 10) + ((4 * Re ** -.33) ** 10) + .4 ** 10
            phi2 = 1 / ((.148 * Re ** .11) ** -10 + (.5) ** -10)
            phi3 = ((Re ** -1.625) * (1.57 * 10 ** 8)) ** 10
            phi4 = 1 / (((6 * 10 ** -17) * Re ** 2.63) ** -10 + (.2 ** -10))

            CD = ((1 / (((phi1 + phi2) ** -1) + (phi3) ** -1)) + phi4) ** (1 / 10)

        return CD

    def myPath(self):

        # Pull atmospheric data
        h, T, g, P, rhof, mu = np.loadtxt('US Standard Air Properties.txt', skiprows=4, unpack=True)

        # Pull wind data
        WS = np.array([row[1] for row in self.windDat])
        windAlt = np.array([row[0] for row in self.windDat])

        # Define regularly used formulas
        R = 287.058  # J/KG*K
        RHelium = 2077.1 # J/KG*K
        vol2 = lambda T2,P2: self.hMass/((rho1*T1*P2) / (T2*P1))
        vol = lambda r: (4 / 3) * mth.pow(r, 3) * mth.pi
        invvol = lambda V: mth.pow(((V * 3) / (4 * mth.pi)), (1 / 3))
        circA = lambda r: mth.pow(r, 2) * mth.pi
        rho = lambda P, T, R: (P) / (R * T)

        # Defining Reference Values(We know radius at sea level therefore, we can determine
        # values anywhere using the ideal gas equation
        h1 = 0
        rhoHSL = .18 #Kg/m^3
        P1 = float(griddata((h), P, (h1)))*10**4
        T1 = float(griddata((h), T, (h1))) + 273
        V1 = vol((self.startR)/2)
        rho1 = rho(P1,T1,RHelium)

        self.hMass = (rho(P1,T1,RHelium))*V1

        # Get cumulative mass
        m = self.balloonM + self.payloadM + self.additionalPayload + self.hMass

        self.save = False

        #ODE for flight path
        def myFlight(X,t):
            rhoFluid = float(griddata((h), rhof, (X[1])))
            P2 = float(griddata((h), P, (X[1])))*10**4
            T2 = float(griddata((h), T, (X[1]))) + 273
            grav = float(griddata((h), g, (X[1])))
            myMu = float(griddata(h,mu,X[1]))*10**-5
            windVel = float(griddata((windAlt), WS, (X[1])))
            V2 = vol2(T2, P2)

            myR = invvol(V2)

            rho2 = rho(P2, T2, RHelium)

            #Gives the initial velocities
            x = X[0]
            y = X[1]
            xdot = X[2]
            ydot = X[3]

            magV = mth.sqrt(((windVel-xdot)**2)+(ydot**2))

            #Get the reynolds number to find the CD
            Re = (rhoFluid*magV*(myR*2))/myMu
            CD = self.myCD(Re)

            #Get the force due to drag
            DX = .5 * rhoFluid * (abs(windVel - xdot))*(windVel - xdot) * CD * circA(myR)
            DY = .5 * rhoFluid * (abs(ydot))*ydot * CD * circA(myR)

            #Horizontal equations
            xddot = DX/m

            #Vertical equation
            yddot = (((rhoFluid)*V2*grav)-DY-m*grav)/m

            if X[1] >= self.finalAlt and self.save == False:
                self.saveR = myR
                self.save = True

            return [xdot,ydot,xddot,yddot]

        #Run the ODE
        self.timeTo = np.linspace(0,int(self.maxTime),int(self.nsteps))
        X = [0,0,0,0]
        ans = odeint(myFlight,X,self.timeTo)

        #Find max altitude and cut off the data
        topI = len(ans[:,0])

        for i in range(len(ans[:,1])):
            if ans[i,1] >= self.finalAlt:
                topI = i
                self.finalTime = self.timeTo[i]
                break

        self.timeTo = self.timeTo[0:i]
        self.postX = ans[0:i,0]
        self.postY = ans[0:i,1]
        self.postVX = ans[0:i, 2]
        self.postVY = ans[0:i, 3]

        pass
def main():
    pullDat = fileExtractor()
    filename = 'Balloon 3.txt'
    f1 = open(filename, 'r')  # open the file for reading
    data = f1.readlines()  # r
    f1.close()
    pullDat.readFileData(data)

    myBalloon = balloon(pullDat, 0, 0)
    myBalloon.myPath()

    # Test plots position over time
    plt.plot(myBalloon.timeTo,myBalloon.postX)
    plt.plot(myBalloon.timeTo, myBalloon.postY)
    plt.xlabel('Distance Across the Ground - m')
    plt.ylabel('Altitude - m')
    plt.title('Predicted Weather Balloon Path')
    plt.show()

    plt.plot(myBalloon.timeTo, myBalloon.postVX)
    plt.plot(myBalloon.timeTo, myBalloon.postVY)
    plt.xlabel('Distance Across the Ground - m')
    plt.ylabel('Altitude - m')
    plt.title('Predicted Weather Balloon Path')
    plt.show()

    plt.plot(myBalloon.postX, myBalloon.postY)
    plt.xlabel('Distance Across the Ground - m')
    plt.ylabel('Altitude - m')
    plt.title('Predicted Weather Balloon Path')
    plt.show()

    print(myBalloon.finalTime)

if __name__ == "__main__":
    main()
