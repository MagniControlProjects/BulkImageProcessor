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
try:
    import os
    import sys
    import traceback
    import json
    import csv
    import datetime
    import threading
    import time
    import copy
except:
    print("Failed to import python built in libraries")
    sys.exit(1)
try:
    from PIL import ImageFont
    from PIL import Image
    from PIL import ImageDraw
except:
    print("Failed to import pillow, please run 'pip install pillow' from command line.")
    sys.exit(1)
try:
    import BrandedImageMaker
except:
    print("Failed to import BrandedImageMaker")
    traceback.print_exc()
    sys.exit(1)

'''
@date : 10/04/2021
@author: George Linsdell

Primary functionality, take an input string of undefined length and convert this sensibly into a 
branded slogan image. Default image size of 2000x2000px ".png" extended bmp file.

'''
THREAD_LIMIT = 8
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

class ImageGeneratorThread(threading.Thread):
    def __init__(
            self,
            QuoteAuthor,
            Id,
            Configuration=DEFAULT_CONFIGURATION_FILE,
            QuoteFonts=None
            ):
        super().__init__()
        self.ImageCompleted = False
        self.Quote = QuoteAuthor[1]
        self.Author = QuoteAuthor[0]
        self.Filename = "Images_MCP\\%s_%s.png"%(Id,self.Author.strip('",.-?!'))
        self.StartTimer =  datetime.datetime.now()
        self.Configuration = Configuration
        self.QuoteFonts = QuoteFonts
        self.Id = Id
        self.QuoteMaker = BrandedImageMaker.SloganMaker(
            FileName=self.Filename,
            FontFolder=self.QuoteFonts,
            ConfigurationFile=Configuration
            )
        FileLoaded = False
        return
        
    def run(self):
        print(f"Generating Image {self.Id}")
        try:
            #print(f"Start Run {self.Id}")
            self.QuoteMaker.run(self.Quote,self.Author)
            #print(f"Write File {self.Id}")
            self.QuoteMaker.WriteFile()
            #print(f"Write Compelte, Dumping time {self.Id}")
            Duration = datetime.datetime.now() - self.StartTimer
            #print("ImageCreation Completed in %s"%str(Duration))
            #print (f"image Completed {self.Id}")
            self.ImageCompleted = True
        except:
            traceback.print_exc()
        return 
    
    def getImageComplete(self):
        return self.ImageCompleted

class ImageThreadMaker():
    def __init__(
            self,
            QuoteConfiguration=DEFAULT_CONFIGURATION_FILE,
            QuoteFile=DEFAULT_QUOTE_FILE,
            QuoteFonts=DEFAULT_FONTS_FOLDER
            ):
        self.NumberExecuting = 0
        self.TotalThreads = 0
        self.Threads = []
        self.Alive = True
        self.QuoteFile = QuoteFile
        self.QuoteConfiguration = QuoteConfiguration
        self.QuoteFonts = QuoteFonts
        self.Quotes = []
        print("threadmaster Created")
        
    def run(self):
        print("ThreadMakerRunning")
        try:
            if os.path.splitext(self.QuoteFile)[1] == ".csv":
                with open (self.QuoteFile,"r") as csvfile:
                    # CSV : Author, Quote
                    self.spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    for row in self.spamreader:
                        self.Quotes.append([row[0],row[1]])
            elif os.path.splitext(self.QuoteFile)[1] == ".json":
                with open (self.QuoteFile,"r") as j_file:
                    j_raw = json.loads(j_file.read())
                    for i in j_raw:
                        self.Quotes.append([i[1],i[0]])
            
            with open (self.QuoteConfiguration,"r") as r_file:
                Configuration = json.loads(r_file.read())
            while self.Alive:
                if self.Quotes == []:
                    self.Alive = False
                else:
                    if self.NumberExecuting >THREAD_LIMIT:
                        time.sleep(0.1)
                    else:
                        for x in range(THREAD_LIMIT - self.NumberExecuting):
                            #print("Creating New Thread")
                            self.Threads.append(ImageGeneratorThread(
                                self.Quotes.pop(0),
                                copy.deepcopy(self.TotalThreads),
                                Configuration=Configuration,
                                QuoteFonts=DEFAULT_FONTS_FOLDER
                                )
                            )
                            self.TotalThreads += 1
                            self.NumberExecuting +=1
                            self.Threads[self.NumberExecuting-1].start()
                    killlist= []
                    for i in range(len(self.Threads)):
                        if self.Threads[i].getImageComplete():
                            print(f"Starting Thread Delete {self.Threads[i].Id}")
                            killlist.append(i)
                            self.Threads[i].join(5)
                            del_thread = self.Threads.pop(i)
                            del (del_thread)
                            self.NumberExecuting -= 1
                            #print(f"Thread Delete Complete {self.Threads[i].Id}")
                            break
                        else:
                            #print(f"Thread Incomplete {self.Threads[i].Id}")
                            pass
                    
        except:
            traceback.print_exc()
        return