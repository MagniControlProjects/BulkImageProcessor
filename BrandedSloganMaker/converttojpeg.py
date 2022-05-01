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
import shutil

#Rename everything to jpg, not png.
for file in os.listdir(os.getcwd()):
    if os.path.isfile(file):
        if file.endswith(".png.jpg"):
            splitter = file.find(".png.jpg")
            moveto = "%s.jpg"%file[:splitter]
        elif file.endswith(".jng.jpg"):
            splitter = file.find(".jng.jpg")
            moveto = "%s.jpg"%file[:splitter]
        else:
            moveto = "%s.jpg"%os.path.splitext(file)[0]
        shutil.move(file,moveto)

#Make 10 dump folders.
for i in range(10):
    if not os.isdir(str(i)):
        os.makedirs(str(i))

for file in os.listdir(os.getcwd()):
    targetfolder = str(file[0:1])
    if os.path.isfile(file):
        shutil.move(file,"%s\\%s"%(targetfolder,file))