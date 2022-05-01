'''
Copyright 2021 George Linsdell

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import sys
import traceback
import json
import csv
import datetime
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import threading
import time
import copy
'''
@date : 22/08/2020
@author: George Linsdell

Primary functionality, take an input string of undefined length and convert this sensibly into a 
branded slogan image. Default image size of 2000x2000px ".png" extended bmp file.

'''

THREAD_LIMIT = 4
DEFAULT_IMAGE_SIZE = (2000,2000) #2000x2000px
DEFAULT_COLOUR = (255,125,255)
DEFAULT_IMAGE_TYPE = "RGBA"
DEFAULT_OUTPUT_FILENAME = "test.png"
DEFAULT_FONT = "arialbd"

if os.getenv("SO_AUTO_HOME") != None:
    currentDirectory = os.getenv("SO_AUTO_HOME")
else:
    currentDirectory = os.getcwd()
sys.path.append(currentDirectory)

DEFAULT_CONFIGURATION_FILE = os.path.join(currentDirectory,"SloganMaker","Configurations","imageConfiguration.json")
DEFAULT_QUOTE_FILE = os.path.join(currentDirectory,"SloganMaker","SampleData","GoodQuotes.json")
DEFAULT_FONTS_FOLDER = os.path.join(currentDirectory,"SloganMaker","Fonts")

class SloganMaker():
    def __init__(
            self,
            ImageSize = DEFAULT_IMAGE_SIZE,
            StartingColour = DEFAULT_COLOUR,
            ImageType = DEFAULT_IMAGE_TYPE,
            FileName = DEFAULT_OUTPUT_FILENAME,
            TargetFont = DEFAULT_FONT,
            ConfigurationFile = DEFAULT_CONFIGURATION_FILE,
            FontFolder=DEFAULT_FONTS_FOLDER
            ):
        self.Errors = False
        self.ImageSize = ImageSize
        self.ImageWidth = ImageSize[0]
        self.ImageHeight = ImageSize[1]
        self.StartingColour = StartingColour
        self.ImageType = ImageType
        self.Filename = FileName
        self.OutputFolder = ""
        self.TargetFont = TargetFont
        self.FontsReady = False
        if type(ConfigurationFile)==type(""):
            self.LoadConfigurationFromFile(ConfigurationFile)
        else:
            self.LoadConfigurationFromDict(ConfigurationFile)
        self.ConfigurationFile = ConfigurationFile
        self.FontFolder = FontFolder
        self.DiscoverFonts()
        
    def LoadConfigurationFromDict(
            self,
            Configuration_Dict
            ):
        '''
        Allow for dynamic loading of configuration from non file source e.g. REST
        '''
        if type(Configuration_Dict) != type ({}):
            print("Submitted Configuration is not dict")
        else:
            self.Configuration = Configuration_Dict
        self.UnpackConfiguration()
        return 
        
    def LoadConfigurationFromFile(
            self,
            ConfigurationFile = "DEFAULT"
            ):
        '''
        Load parameters from a preset configuration file to avoid repeat value assignment
        '''
        if ConfigurationFile == "DEFAULT":
            ConfigurationFile = self.ConfigurationFile
        print(f"Attempting to open configuration file at '{ConfigurationFile}'")
        with open (ConfigurationFile,"r") as r_file:
            try:
                self.Configuration = json.loads(r_file.read())
            except:
                print("Failed to read configuration with exception")
                traceback.print_exc()
                self.Configuration = {}
                
        try:
            self.UnpackConfiguration()
        except:
            print("Configuration Errors present.")
        return
        
    def UnpackConfiguration(self):
        '''
        Unpack the configuration so object contains the relevant parameters the key elements.
        '''
        try:
            self.StartingColour = tuple(self.Configuration["Background"]["Colour"])
        except:
            traceback.print_exc()
            print("Colour not set in configuration")
        try:
            self.FontColour = tuple(self.Configuration["Font"]["Colour"])
        except:
            print("Unable to determine Font Colour")
            self.FontColour = (255,255,255)
        try:
            self.TargetFont = self.Configuration["Font"]["Name"]
        except:
            print("Unable to determine Font Colour")
            self.TargetFont = DEFAULT_FONT
            
        try:
            self.OutputFolder = self.Configuration["Output"]["path"]
            self.Filename = os.path.join(self.OutputFolder,os.path.split(self.Filename)[1])
            if not os.path.isdir(self.OutputFolder):
                os.makedirs(self.OutputFolder)
        except:
            pass
            
        return
    
    def LoadBrandedImage(self):
        '''
        Load Branded Image, 
        Resize to meet configuration parameters
        '''
        Complete = True
        try:
            self.LogoConfiguration = self.Configuration["logo"]
            #Values are factors not abs, so treat them hat way. 
            self.LogoWidthMax = self.LogoConfiguration["size"]/100 * self.ImageWidth
            self.LogoHeightMax = self.LogoConfiguration["size"]/100 * self.ImageHeight
        except:
            print(f"Exception Occured when trying to draw logo {traceback.format_exc()}")
            return False
        try:
            LogoRaw = Image.open(self.LogoConfiguration["path"])
        except FileNotFoundError:
            print(f"Raw Logo Image in accessible at {self.LogoConfiguration['path']}")
            return False
        LogoWidth,LogoHeight = LogoRaw.size
        if LogoWidth >= LogoHeight:
            #Use Width by default, if it's the same it doesn't matter so 
            #still use width
            Max = 0 #Width
        else:
            Max = 1 # Height
        
        FactorH = LogoHeight/self.LogoHeightMax
        FactorW = LogoWidth/self.LogoWidthMax
        Factors = [FactorW,FactorH]
        
        OutputSize = (round(LogoWidth/Factors[Max]),round(LogoHeight/Factors[Max]))
        self.ResizedLogo = LogoRaw.resize(OutputSize)
        Complete = True
        return Complete
    
    def PlaceResizedLogo(self):
        '''
        Resizing is generated on loading the logo.
        This must consider the placement options.
        '''
        Complete = False
        try:
            LogoAlignX = self.LogoConfiguration["alignX"]
            LogoAlignY = self.LogoConfiguration["alignY"]
        except:
            traceback.print_exc()
            print("Unable to determine alignment Parameters, not Applying")
            return False
        AlignXList = ["left","right","middle"]
        AlignYList = ["top","bottom","centre"]
        if not (LogoAlignX.lower() in AlignXList):
            print("AlignX %s, Not in options %s"%(LogoAlignX,AlignXList))
            return False
        if not (LogoAlignY.lower() in AlignYList):
            print("AlignX %s, Not in options %s"%(LogoAlignY,AlignYList))
            return False
        
        if LogoAlignX.lower() == "left":
            LogoAlignX = 0
        elif LogoAlignX.lower() == "middle":
            LogoAlignX = round((self.ImageWidth/2)-(self.ResizedLogo.size[0]/2))
        elif LogoAlignX.lower() == "right":
            LogoAlignX = round((self.ImageWidth)-(self.ResizedLogo.size[0]))
        
        if LogoAlignY.lower() == "top":
            LogoAlignY = 0
        elif LogoAlignY.lower() == "centre":
            LogoAlignY = round((self.ImageHeight/2)-(self.ResizedLogo.size[1]/2))
        elif LogoAlignY.lower() == "bottom":
            LogoAlignY = round((self.ImageHeight)-(self.ResizedLogo.size[1]))
        #print("Placing the Logo at (%s,%s)"%(LogoAlignX,LogoAlignY))
        #Paste this into the canvas
        self.Canvas.paste(self.ResizedLogo,(LogoAlignX,LogoAlignY),self.ResizedLogo)
        Complete=True
        return Complete
    
    def FixTransparency(
            self,
            GivenImage
            ):
        '''
        VOID. Need to make sure the mask is present when using the resized image
        PNG transparency needs to reapplied using pillow.
        '''
        newData = []
        oldData = GivenImage.getdata()
        for item in oldData:
            if item[0] != 0:
                print("suh")
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
            #if item[3] ==0:
                newData.append((255, 0, 255, 0))
            else:
                newData.append(item)
        
        GivenImage.putdata(newData)
        GivenImage.show()
        return GivenImage
    
    def DiscoverFonts(self):
        '''
        Assume this is a windows machine for this minute:
        Support Linux font selection or embed specific ones.
        '''
        if not self.FontsReady:
            self.Fonts = {}
            for path in [
                #"C:\\Windows\\Fonts",
                self.FontFolder
                ]:
                for font in os.listdir(path):
                    try:
                        FontName,FontExt = os.path.splitext(font.lower())
                    except:
                        traceback.print_exc()
                        continue
                    if FontExt == ".otf":
                        self.Fonts[FontName] = os.path.join(path,font)
                    elif FontExt == ".ttf":
                        self.Fonts[FontName] = os.path.join(path,font)
                    else:
                        #print ("%s is not a font."%font)
                        pass
            #print("Discovered %s Fonts"%len(self.Fonts))
            with open ("font.json","w") as o_file:
                o_file.write(json.dumps(self.Fonts, sort_keys=True))
            self.FontsReady = True
        return
        
    def run(
            self,
            TextString,
            Author = None
            ):
        '''
        Run will create a image dependent on the configuration
        '''
        #print("Creating Base Image")
        if not self.CreateImageBase():
            print("failed to create Image Canvas")
            return
        #print("Drawing Background Image")
        self.DrawBackGround()
        try:
            #print("Drawing Text")
            self.DrawText(TextString)
        except:
            traceback.print_exc()
        #print("Drawing Header")
        self.DrawHeader(self.Configuration["Header"]["Text"])
        if Author != None:
            #print("draw Author")
            if not self.DrawAuthor(Author):
                print("Failed to generate Authors name")
        #print("Drawing Branded Image")
        if not self.LoadBrandedImage():
            print("Failed to Draw Branded Image, Check Configuration")
        
        #print("PLacing Resized Logo")
        if not self.PlaceResizedLogo():
            print("Failed to Place Resized Logo")
        return
        
    def DrawBackGround(self):
        '''
        Draw the background?
        '''
        self.ActiveCanvas = ImageDraw.Draw(self.Canvas)
        return
        
    def DrawText(
            self,
            InputText
            ):
        '''
        Draw Text on the document from the quote input file.
        '''
        self.font = ImageFont.truetype(self.Fonts[self.Configuration["Font"]["Name"]], self.Configuration["Font"]["Size"])
        YMin = self.ImageHeight * (self.Configuration["Borders"][2] /100)
        YMax = self.ImageHeight * (self.Configuration["Borders"][3] /100)
        XMin = self.ImageHeight * (self.Configuration["Borders"][0] /100)
        XMax = self.ImageHeight * (self.Configuration["Borders"][1] /100)
        
        MaxWidth = XMax-XMin
        MaxHeight = YMax - YMin
        ProcessComplete = False
        Words = InputText.split(" ")
        TotalWords = len(Words)
        WordsDeployed = 0   
        Lines = []
        while not ProcessComplete:
            Joinlist = []
            ExitLoop = False
            while not ExitLoop:
                NewString = ""
                Joinlist.append(WordsDeployed)
                WordsDeployed +=1
                for i in Joinlist:
                    NewString = NewString + Words[i] + " "
                try:
                    if self.font.getsize(NewString)[0] > MaxWidth:
                        if len(Joinlist)>1:
                            Joinlist.pop(-1)
                            WordsDeployed -= 1
                            NewString = ""
                            for i in Joinlist:
                                NewString = NewString + Words[i] + " "
                            ExitLoop = True
                        else:
                            ExitLoop = True
                except OSError:
                    print("Failed to process font.")
                    ExitLoop = True
                    self.Errors = True
                    traceback.print_exc()
                except:
                    traceback.print_exc()
                if WordsDeployed == TotalWords:
                    ExitLoop = True
            Lines.append(NewString)
            if WordsDeployed == TotalWords:
                ProcessComplete = True
        self.TextRows = len(Lines)
        if self.TextRows > 8:
            print("Skipping as more than 8 lines")
            return 
        RowHeight = (MaxHeight/self.TextRows)
        textheight = self.font.getsize("test")[1]
        for i in range(self.TextRows):
            if i == 0:
                Lines[i] = '"'+Lines[i]
            elif i == self.TextRows -1:
                Lines[i] = Lines[i]+'"'
            YPosition = YMin + (textheight*i)
            self.DrawTextLine(
                Lines[i],
                YPosition
                )
        return
        
    def DrawAuthor(
            self,
            TargetText
            ):
        '''
        Try to clean up the formatting of the author string.
        '''
        try:
            CurrentFontSize = self.Configuration["Font"]["Size"]
            self.Authorfont = ImageFont.truetype(
                self.Fonts[self.Configuration["Font"]["Name"]],
                CurrentFontSize
                )
            if TargetText == '""':
                TargetText = "Unknown"
            
            self.HeaderFont = ImageFont.truetype(self.Fonts[self.Configuration["Header"]["Font"]], round(self.Configuration["Header"]["Size"]))
            MaxAuthorWidth = 0.5* self.ImageWidth
            try:
                MaxAuthorWidth = self.Configuration["Author"]["WidthPercent"]*(self.ImageWidth*0.01)
            except:
                print("Author,WidthPercent not set, defaulting to 50%")
            
            TooBig = True
            while TooBig:
                if self.Authorfont.getsize(TargetText)[0] > MaxAuthorWidth:
                    CurrentFontSize -= 2
                    self.Authorfont = ImageFont.truetype(
                    self.Fonts[self.Configuration["Font"]["Name"]],
                        CurrentFontSize
                        )
                    #print( f"{self.Authorfont.size} - {self.Authorfont.getsize(TargetText)[0]}")
                elif CurrentFontSize < 0 :
                    print("Unable to auto scale, using original size.")
                else:
                    TooBig = False
            #writesize = self.font.getsize()
            AuthorText = "Author - \n%s:"%TargetText.strip('"')
            textwidth = self.Authorfont.getsize(AuthorText)[0]
            AlignX = self.ImageSize[0]-(self.ImageSize[0]*0.95)
            AlignY = self.ImageSize[1] - (self.ImageSize[1]/8) - self.HeaderFont.getsize("test")[1]
            testwrite = self.ActiveCanvas.text(
                (AlignX, AlignY),
                AuthorText,
                self.FontColour,
                font=self.Authorfont
                )
            return True
        except:
            traceback.print_exc()
            return False
    
    def DrawHeader(
            self,
            TargetText
            ):
        '''
        Optional header by passing 
        "Header":{
            "Text":"Quote Of The Day",
            "Font":"gothamcondensed-bold",
            "Size":180
        },
        Object in configuration file.
        '''
        self.HeaderFont = ImageFont.truetype(self.Fonts[self.Configuration["Header"]["Font"]], round(self.Configuration["Header"]["Size"]))
        #writesize = self.font.getsize(TargetText)
        AlignX = (self.ImageSize[0]/8)
        AlignY = (self.ImageSize[1]/20)
        testwrite = self.ActiveCanvas.text(
            (AlignX, AlignY),
            TargetText,
            self.FontColour,
            font=self.HeaderFont
            )
        return
        
    def DrawTextLine(
            self,
            TargetText,
            YPosition,
            
            ):
        '''
        Draw a single Text Line, central in X, at a specific Y Offset
        '''
        writesize = self.font.getsize(TargetText)
        CentreAlignX = (self.ImageSize[0]/2)-(writesize[0]/2)
        testwrite = self.ActiveCanvas.text(
            (CentreAlignX, YPosition),
            TargetText,
            self.FontColour,
            font=self.font
            )
        return
        
    def CreateImageBase(self):
        '''
        Create the base Image 
        '''
        try:
            self.Canvas = Image.new(
                self.ImageType,
                self.ImageSize,
                self.StartingColour
                )
            self.DrawBackGround()
        except:
            traceback.print_Exc()
            return False
        return True
    
    def SetFileName(
            self,
            FileName
            ):
        self.Filename = FileName
        self.ExportFolder = os.path.split(self.Filename)[0]
        if not os.path.isdir(self.ExportFolder):
            os.makedirs(self.ExportFolder)
        return
    
    def WriteFile(self):
        print("Writing File to %s"%os.path.join(currentDirectory,self.Filename))
        try:
            self.Canvas.save(self.Filename)
        except OSError:
            print(f"failed to save canvas {self.Filename}")
        return


    
if __name__ == '__main__':
    TotalStartTimer =  datetime.datetime.now()
    runner = ImageThreadMaker()
    runner.run()
    Duration = datetime.datetime.now() - TotalStartTimer
    print("Total Image creation of %s images complete in %s"%(runner.TotalThreads,str(Duration)))

