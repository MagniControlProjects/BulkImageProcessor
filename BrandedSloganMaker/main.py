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
    import sys
    import os
    import datetime
    import csv
    import json
    import traceback
    import argparse
except:
    print("Failed to import Python Built in libraries")
    sys.exit(1)

'''
@author: George Linsdell
@date: 07/04/2021

Entry Level script for generating social media style images from csv or json string data.
'''

if os.getenv("SO_AUTO_HOME") != None:
    currentDirectory = os.getenv("SO_AUTO_HOME")
else:
    currentDirectory = os.getcwd()
sys.path.append(currentDirectory)

try:
    import BrandedImageMaker
    import BrandedImageThreader
except:
    print("Failed to import MCP Specific modules.")
    sys.exit(1)

THREAD_MODES = [
    "SINGLETHREADED",
    "MULTITHREADED"
]
DEFAULT_CONFIGURATION_FILE = os.path.join(
    currentDirectory,
    "SloganMaker",
    "Configurations",
    "imageConfiguration.json"
    )
DEFAULT_QUOTE_FILE = os.path.join(
    currentDirectory,
    "SloganMaker",
    "SampleData",
    "GoodQuotes.json"
    )
DEFAULT_FONTS_FOLDER = os.path.join(
    currentDirectory,
    "SloganMaker",
    "Fonts"
    )

def main(args):
    inputfile = args.quotepath
    ThreadMode = THREAD_MODES[int(args.MultiThread)]

    print("Starting Generation of Branded Images")
    TotalStartTimer =  datetime.datetime.now()
    if ThreadMode == "MULTITHREADED":
        print("Running as Multi threaded entity.")
        runner = BrandedImageThreader.ImageThreadMaker(
            QuoteConfiguration=DEFAULT_CONFIGURATION_FILE,
            QuoteFonts=DEFAULT_FONTS_FOLDER,
            QuoteFile=DEFAULT_QUOTE_FILE
            )
        runner.run()
        Duration = datetime.datetime.now() - TotalStartTimer
        print("Total Image creation of %s images complete in %s"%(
            runner.TotalThreads,
            str(Duration)
            )
        )
        numberOfFiles = runner.TotalThreads
    else:
        print ("Running as Single Threaded entity.")
        TotalStartTimer =  datetime.datetime.now()
        numberOfFiles = 0
        MakerBot = BrandedImageMaker.SloganMaker(
            FileName="Images\\%s.png"%numberOfFiles,
            ConfigurationFile=DEFAULT_CONFIGURATION_FILE,
            FontFolder=DEFAULT_FONTS_FOLDER,
            )#QuoteFile=DEFAULT_QUOTE_FILE)
        print("Loading from file %s"%inputfile)
        if os.path.splitext(inputfile)[1] == ".csv":
            with open (inputfile,"r") as csvfile:
                spamreader = csv.reader(
                    csvfile,
                    delimiter=',',
                    quotechar='"'
                    )
                for row in spamreader:
                    StartTimer =  datetime.datetime.now()
                    MakerBot.SetFileName(
                        FileName="Image\\%s_%s.png"%(
                            numberOfFiles,
                            row[0].strip('",.-')
                            )
                        )
                    MakerBot.run(
                        row[1],
                        row[0]
                        )
                    MakerBot.WriteFile()
                    numberOfFiles += 1
                    Duration = datetime.datetime.now() - StartTimer
                    print("ImageCreation Completed in %s"%str(Duration))
                    print(Duration)
                    
        elif os.path.splitext(inputfile)[1] == ".json":
            with open (inputfile,"r") as r_file:
                catalogue = json.loads(r_file.read())
                for row in catalogue:
                    StartTimer =  datetime.datetime.now()
                    MakerBot.SetFileName(
                        FileName="Image\\%s_%s.png"%(
                            numberOfFiles,
                            row[0].strip('",.-')
                            )
                        )
                    MakerBot.run(
                        row[0],
                        row[1]
                        )
                    MakerBot.WriteFile()
                    numberOfFiles += 1
                    Duration = datetime.datetime.now() - StartTimer
                    print("ImageCreation Completed in %s"%str(Duration))
                    print(Duration)
        Duration = datetime.datetime.now() - TotalStartTimer
        print("Total Image creation of %s images complete in "%numberOfFiles)
        print(Duration)
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Initialising Slogan Maker Tool."
        )
    
    parser.add_argument('--quotepath', nargs='?', default = DEFAULT_QUOTE_FILE, help = 'Path to the Quote File Path.')
    parser.add_argument('--MultiThread', nargs='?', default = 0, help = '0=Single Threaded, 1=MultiThread')
    
    args = parser.parse_args()
    sys.exit(main(args))
    