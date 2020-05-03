# Code by Spencer Lankford

class fileExtractor:
    def __init__(self):
        self.title = None

        #Order of Array: Balloon,Launch Diameter,glider,wind,payload,altitude
        self.simRequest = [None,None,None,None,None,None]

        #Order of Array: maxtime,nsteps
        self.simControl = [None,None]

        self.balloonOptions = []

        self.windOptions = []

        self.gliderOptions = []

        #Order of Array:   S,AR,e,m,Cdo
        self.gliderDat = [None,None,None,None,None]

        #Order of Array: 2D Array, col 0 = alt, col 1 = wind speed
        self.windDat = []

        #Order of Array: ID,Mass,UninflatedDiam,Burstdiam
        self.balloonDat = [None,None,None,None]


    def readFileData(self, data):
        # data is an array of strings, read from a Truss data file
        try:
            for line in data:  # loop over all the lines
                # replace leading whitespace, quotes and parentheses
                line = line.strip().replace("'", "").replace('"', '').replace("(", "").replace(")", "")

                # split the line at commas
                cells = line.split(',')

                # convert everything to lowercase
                keyword = cells[0].lower()

                if keyword == 'title':
                    self.title = cells[1].replace("'","")
                if keyword == 'simulation'and self.simRequest[0] == None:
                    self.simRequest[0] = cells[1].replace("'", "").replace("    ","")
                    self.simRequest[1] = cells[2].replace("'", "").replace(" ","")
                    self.simRequest[2] = cells[3].replace("'", "").replace("   ","")
                    self.simRequest[3] = cells[4].replace("'", "").replace(" ","")
                    self.simRequest[4] = float(cells[5].replace("'", "").replace(" ",""))
                    self.simRequest[5] = float(cells[6].replace("'", "").replace(" ", ""))

                if keyword == 'simcontrol' and self.simRequest[0] != None and self.simControl[0] == None:
                    self.simControl[0] = float(cells[1].replace("'", "").replace(" ", ""))
                    self.simControl[1] = float(cells[2].replace("'", "").replace(" ", ""))
                if keyword == 'glider' and self.simRequest[2] == cells[1].replace("   ","") and self.simRequest[0] != None:
                    self.gliderDat[0] = float(cells[2].replace("'", "").replace(" ",""))
                    self.gliderDat[1] = float(cells[3].replace("'", "").replace(" ",""))
                    self.gliderDat[2] = float(cells[4].replace("'", "").replace(" ",""))
                    self.gliderDat[3] = float(cells[5].replace("'", "").replace(" ",""))
                    self.gliderDat[4] = float(cells[6].replace("'", "").replace(" ",""))
                elif keyword == 'windlib' and self.simRequest[3] == cells[1].replace(" ","") and self.simRequest[0] != None:
                    for x in range(2,len(cells),2):
                        self.windDat.append([float(cells[x].replace(" ","")),float(cells[x+1].replace(" ",""))])
                elif keyword == 'balloonlib' and self.simRequest[0].replace(" ","") == cells[1].replace(" ","") and self.simRequest[0] != None:
                    self.balloonDat[0] = (cells[1].replace("'", "").replace('   ',''))
                    self.balloonDat[1] = float(cells[2].replace("'", "").replace(" ",""))
                    self.balloonDat[2] = float(cells[3].replace("'", "").replace(" ",""))
                    self.balloonDat[3] = float(cells[4].replace("'", "").replace(" ",""))
                if keyword == 'balloonlib':
                    self.balloonOptions.append(cells[1].replace("'", "").replace('   ',''))
                elif keyword == 'glider':
                    self.gliderOptions.append(cells[1].replace("'", "").replace('   ',''))
                elif keyword == 'windlib':
                    self.windOptions.append(cells[1].replace("'", "").replace('   ','').replace(" ",""))

            #Prioritizes the default sim info to the top of options
            priLoc = self.balloonOptions.index(self.simRequest[0])
            saveMe = self.balloonOptions[0]
            self.balloonOptions[0] = self.balloonOptions[priLoc]
            self.balloonOptions[priLoc] = saveMe

            priLoc = self.gliderOptions.index(self.simRequest[2])
            saveMe = self.gliderOptions[0]
            self.gliderOptions[0] = self.gliderOptions[priLoc]
            self.gliderOptions[priLoc] = saveMe

            priLoc = self.windOptions.index(self.simRequest[3])
            saveMe = self.windOptions[0]
            self.windOptions[0] = self.windOptions[priLoc]
            self.windOptions[priLoc] = saveMe

        except:
            print('File Read Error, Check That All Required Data is Present')
def main():
    # get the filename using the OPEN dialog
    filename = 'Balloon 2.txt'
    f1 = open(filename, 'r')  # open the file for reading
    data = f1.readlines()  # read the entire file as a list of strings
    myBoy = fileExtractor()
    myBoy.readFileData(data)
    f1.close()  # close the file  ... very important

    plz = fileExtractor()  # create a plz instance (object)
    plz.readFileData(data)

    print(plz.title)
    print(plz.simRequest)
    print(plz.simControl)
    print(plz.gliderDat)
    print(plz.windDat)
    print(plz.balloonDat)
    print(plz.balloonOptions)
    print(plz.windOptions)
    print(plz.gliderOptions)

if __name__ == "__main__":
    main()
