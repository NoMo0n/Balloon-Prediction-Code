# Code by Allan Burba

import numpy as np
from scipy.optimize import minimize
from scipy.integrate import odeint
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

from FileExtractor import fileExtractor
from BalloonClass import balloon

class Glider:
    def __init__(self, myFile):
        # Initialization Step
        # myFile is to get data from file reader
        self.S = myFile.gliderDat[0]
        self.AR = myFile.gliderDat[1]
        self.e = myFile.gliderDat[2]
        self.m = myFile.gliderDat[3]
        self.CDo = myFile.gliderDat[4]
        self.finalAlt = myFile.simRequest[5]
        self.maxTime = myFile.simControl[0]
        self.npoints = myFile.simControl[1]
        self.windDat = myFile.windDat
        self.t = 0
        self.xy = None
        self.x = []
        self.y = []
        self.maxTGlider = 0

        h, T, g, P, rhof, mu = np.loadtxt('US Standard Air Properties.txt', skiprows=4, unpack=True)
        self.atmosphere = [h,T,g,P,rhof]


    def Peformance(self, Alpha, gc, rho, payload, windspeed):
        Eps = 1 / (np.pi * self.e * self.AR)
        CLa = np.pi * self.AR / (1 + np.sqrt(1 + (self.AR / 2) ** 2))
        CL = CLa * Alpha
        CD = self.CDo + Eps * CL ** 2
        tmass = self.m + payload

        num = 4 * gc ** 2 * tmass ** 2
        denom = (CD * self.S * rho) ** 2 + (CL * self.S * rho) ** 2
        V = (num / denom) ** 0.25
        Gam = -np.arcsin((0.5 * CD * self.S * V ** 2 * rho) / (gc * tmass))
        xdot = V * np.cos(Gam)
        ydot = V * np.sin(Gam)
        glideRatio = - (xdot - windspeed) / ydot
        groundSpeed = xdot - windspeed
        return xdot, ydot, glideRatio, groundSpeed

    def MaxGlideRatio(self, gc, rho, payload, windspeed, AlpaGuess):
        def objective(Alpha):
            glideRatio = self.Peformance(Alpha[0], gc, rho, payload, windspeed)[2]
            return -glideRatio

        ans = minimize(objective, [AlpaGuess], method='Nelder-Mead')
        return float(ans.x), -ans.fun

    def ReturnHome(self, altitude, distance,  winds, payload, maxtime, npoints):
        WS = np.array([row[1] for row in winds])
        windAlt = np.array([row[0] for row in winds])
        def ode_system(X,t):
            nonlocal AlphaGuess
            x = X[0]; y = X[1];

            atm = self.atmosphere

            if y < 0: y = 0
            windspeed = float(griddata(windAlt, WS,y))
            gc = float(griddata(atm[0], atm[2], y))
            rho = float(griddata(atm[0], atm[4],y))

            Alpha = self.MaxGlideRatio(gc, rho, payload, windspeed, AlphaGuess)[0]
            AlphaGuess = Alpha
            xdot, ydot, glideRatio, groundSpeed = self.Peformance(Alpha,gc,rho,payload,windspeed)

            return [-groundSpeed,ydot]

        AlphaGuess = 0.1

        t = np.linspace(0,int(maxtime),int(npoints))
        self.t = t
        ic = [distance,altitude]
        self.xy = RK4(ode_system,ic,t)
        for i in range(len(self.xy)):
            if self.xy[i,1] <= 0:
                savei = i
                break
        self.x = self.xy[0:i,0]
        self.y = self.xy[0:i,1]
        self.t = self.t[0:i]
        self.maxTGlider = max(self.t)

class Wind:
    def __init__(self):
        self.name = None
        self.altitudes = []
        self.speeds = []
class Balloon:
    def __init__(self):
        self.name = None
        self.mass = None
        self.uninflatedDia = None
        self.burstDia = None

# class Atmosphere:
#     def __init__(self):

def FindAltitudeIndex(xy,altitude):
    for i in range(len(xy)):
        if xy[i,2] > altitude:
            return i
        return len(xy)-1

def gasVolume(pressure,mass,R,T):
    vol = mass * R * T / pressure
    return vol

def gasMass(pressure,volume,R,TC):
    T = TC + 273.15
    mass = pressure * volume / R /TC
    return mass


def myCD(Re):
    # Initialize phi variables
    # NOTE: This equation was found in the research
    # paper provided on canvas
    if Re < .01:
        return 100
    else:
        phi1 = ((25 * Re ** -1) ** 10) + ((21 * Re ** -.67) ** 10) + ((4 * Re ** -.33) ** 10) + .4 ** 10
        phi2 = 1 / ((.148 * Re ** .11) ** -10 + (.5) ** -10)
        phi3 = ((Re ** -1.625) * (1.57 * 10 ** 8)) ** 10
        phi4 = 1 / (((6 * 10 ** -17) * Re ** 2.63) ** -10 + (.2 ** -10))

        CD = ((1 / (((phi1 + phi2) ** -1) + (phi3) ** -1)) + phi4) ** (1 / 10)

    return CD

def RK4(func,ic,t):
    ntimes = len(t)
    nstates = len(ic)
    x = np.zeros((ntimes,nstates))
    x[0] = ic
    for i in range(len(t)-1):
        h = t[i+1] - t[i]
        k1 = h*np.array(func(x[i],t[i]))
        k2 = h * np.array(func(x[i] + k1 / 2, t[i] + h / 2))
        k3 = h * np.array(func(x[i] + k2 / 2, t[i] + h / 2))
        k4 = h * np.array(func(x[i] + k3, t[i] + h))
        x[i + 1] = x[i] + (1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        pass
    return x

def main():
    pullDat = fileExtractor()
    filename = 'Balloon 3.txt'
    f1 = open(filename, 'r')  # open the file for reading
    data = f1.readlines()  # r
    f1.close()
    pullDat.readFileData(data)
    aBalloon = balloon(pullDat)
    aBalloon.myPath()

    myBalloon = Glider(pullDat)
    #myBalloon.ReturnHome(max(aBalloon.postX), pullDat.simRequest[4])
    myBalloon.ReturnHome(max(aBalloon.postY),max(aBalloon.postX),pullDat.windDat,pullDat.simRequest[4],pullDat.simControl[0],pullDat.simControl[1])
    x = myBalloon.xy[:, 0]
    y = myBalloon.xy[:, 1]
    plt.plot(myBalloon.x, myBalloon.y)
    # plt.xlabel('Distance Across the Ground - m')
    # plt.ylabel('Altitude - m')
    # plt.title('Predicted Weather Balloon Path')
    plt.show()
    # Test plots position over time

if __name__ == "__main__":
    main()