'''
Copyright 2022 George Linsdell

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
    import time
    import csv
    import json
    import traceback
    import argparse
except:
    print("Failed to import Python Built in libraries")
    sys.exit(1)

'''
@author: George Linsdell
@date: 02/05/2022

Entry Level script for watermarking all images located in the "inputFolder" or parent folder.
'''

if os.getenv("SO_AUTO_HOME") != None:
    currentDirectory = os.getenv("SO_AUTO_HOME")
else:
    currentDirectory = os.getcwd()
sys.path.append(currentDirectory)

try:
    import WatermarkMarker
except:
    print("Failed to import WaterMarker.")
    sys.exit(1)

THREAD_MODES = [
    "SINGLETHREADED",
    "MULTITHREADED"
]
WatchFolder = os.path.join(
    os.path.split(currentDirectory)[0],
    "InputFolder"
    )
OutputFolder = os.path.join(
    os.path.split(currentDirectory)[0],
    "OutputFolder"
    )

def main(args):
        TotalStartTimer = time.time()
        with open(args.config,"r") as r_file:
            Configuration = json.loads(r_file.read())
        numberOfFiles = 0
        Executors = []
        for root,dirs,files in os.walk(WatchFolder):
            for i_file in files:
                if os.path.splitext(i_file)[1].lower() in [".jpg","jpeg"]:
                    FileToProcess = os.path.join(root,i_file)
                    print(f"Processing {FileToProcess}")
                    Executors.append(
                        WatermarkMarker.WatermarkMarker(
                            Configuration["Watermark"],
                            FileToProcess)
                        )
                    OutputPath = os.path.join(OutputFolder,i_file)
                    Executors[-1].run(OutputPath)
                    numberOfFiles += 1
        Duration = time.time() - TotalStartTimer
        print("Total Image creation of %s images complete in "%numberOfFiles)
        print(Duration)
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Initialising Slogan Maker Tool."
        )
    parser.add_argument('--config', nargs="?", default = "DEFAULT", help = "path to watermarking configuration file.")
    parser.add_argument('--MultiThread', nargs='?', default = 0, help = '0=Single Threaded, 1=MultiThread')
    
    args = parser.parse_args()
    sys.exit(main(args))
    