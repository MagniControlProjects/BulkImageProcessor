import os
import sys
try:
    from PIL import ImageFont
    from PIL import Image
    from PIL import ImageDraw
except:
    print("Failed to import pillow, please run 'pip install pillow' from command line.")
    
class WatermarkMarker():
    def __init__(
            self,
            Configuration,
            InputImage
            ):
        '''
        Take JSON configuration and absolute input image path.
        '''
        self.Configuration = Configuration
        self.InputImage = InputImage
    
    def InterpretConfiguration(self):
        '''
        Draw Text on the document from the quote input file.
        '''
        self.AlignmentX = self.Configuration["Alignment"]["Horizontal"]
        self.AlignmentY = self.Configuration["Alignment"]["Vertical"]
        try:
            self.Padding = self.Configuration["Alignment"]["Padding"]
        except:
            self.Padding = [10,10,10,10] # [top, bottom, left, right]
        self.MarkType = self.Configuration["MarkType"]
        if self.MarkType == "Text":
            #Size = Font Size
            self.FontName = os.path.join(os.getcwd(),"Fonts",self.Configuration["Font"])
            self.FontFile = os.path.join(os.getcwd(),"Fonts",self.Configuration["FontFile"])
            self.Size = self.Configuration["Size"]
            self.WatermarkText = self.Configuration["Text"]
        if self.MarkType == "Image":
            #Size = Percentage of total 
            self.ImageFile = self.Configuration["Path"]
            self.Scale = self.Configuration["Scale"]
            #self.PreserveColours = self.Configuration["PreserveColours"]
        self.MaskFormat = "P" #Palette
        try:
            self.LimitX = self.Configuration["HorizontalLimit"]
        except:
            self.LimitX = 65535
        try:
            self.LimitY = self.Configuration["VerticalLimit"]
        except:
            self.LimitY = 65535
        
    def InterpretImage(self):
        with Image.open(self.InputImage) as I_Image:
            self.ImageWidth,self.ImageHeight = I_Image.width,I_Image.height
        print(f"Image is w:{self.ImageWidth}px h:{self.ImageHeight}px")
        return
        
    def CalculateGeometry(self):
        '''
        Workout where the text is going to land. Using adobes definition for alignment.
        '''
        
        if self.MarkType == "Text":
            self.Font = ImageFont.truetype(self.FontFile,self.Size)
            self.MarkWidth,self.MarkHeight = self.Font.getsize(self.WatermarkText)
        elif self.MarkType == "Image":
            with Image.open(self.ImageFile) as WM_Image:
                WM_Image = WM_Image.resize((int(WM_Image.width*self.Scale),int(WM_Image.height*self.Scale)))
                self.MarkWidth,self.MarkHeight = WM_Image.width,WM_Image.height
        
        #Determine X
        if self.AlignmentX.upper() == "Middle" or self.AlignmentX.upper() == "CENTER":
            self.DrawX = (self.ImageWidth/2) - (self.MarkWidth/2)
            print ("Aligning X Middle")
        elif self.AlignmentX.upper() == "RIGHT":
            print ("Aligning Y Right")
            self.DrawX = self.ImageWidth - self.MarkWidth - self.Padding[3]
        elif self.AlignmentX.upper() == "LEFT":
            print ("Aligning Y Left")
            self.DrawX = 0 + self.Padding[2]
            
        #Determine Y Draw Position
        if self.AlignmentY.upper() == "MIDDLE" or self.AlignmentY.upper() == "CENTER":
            print ("Aligning Y Centre")
            self.DrawY = (self.ImageHeight/2) - (self.MarkHeight/2)
        elif self.AlignmentY.upper() == "BOTTOM":
            print ("Aligning Y Bottom")
            self.DrawY = self.ImageHeight - self.MarkHeight - self.Padding[1]
        elif self.AlignmentY.upper() == "TOP":
            print ("Aligning Y Bottom")
            self.DrawY = 0 + self.Padding[0]
        print (f"DrawX = {self.DrawX}, DrawY = {self.DrawY}")
        return
    
    def GenerateMark(self):
        MaskOutput = Image.new("P",(self.ImageWidth,self.ImageHeight),color = 255)
        Drawable = ImageDraw.Draw(MaskOutput)
        ActualOutput =  Image.open(self.InputImage)
        DrawOut = ImageDraw.Draw(ActualOutput)
        if self.MarkType == "Text":
            Drawable.text((self.DrawX,self.DrawY),self.WatermarkText,fill=0,font=self.Font)
        
        if self.MarkType == "Image":
            MaskInput = Image.open(self.ImageFile)
            if self.Scale != 1:
                print("Doing Resize")
                MaskInput = MaskInput.resize(
                    (int(MaskInput.width*self.Scale),int(MaskInput.height*self.Scale))
                     )
            for px_X in range(MaskInput.width):
                for px_Y in range(MaskInput.height):
                    Pixel = MaskInput.getpixel((px_X,px_Y))
                    if Pixel[0] > 50 or Pixel[1] > 50 or Pixel[2] > 50: #Check > 50 for aliasing.
                        Drawable.point((px_X,px_Y),fill=0)
                        DrawOut.point((px_X+self.DrawX,px_Y+self.DrawY),Pixel)
        MaskOutput.save(self.MaskPath)
        ActualOutput.crop((0,0,self.ImageWidth,self.ImageHeight))
        ActualOutput.save(self.OutputPath)
        return 
        
    def run(
            self,
            OutputPath
            ):
        BaseName,ExtName = os.path.splitext(OutputPath)
        MaskName = f"{BaseName}_mask"
        OutName = f"{BaseName}_WaterMarked"
        self.OutputPath = OutName + ExtName
        self.MaskPath = MaskName + ".tif"
        
        self.InterpretConfiguration()
        self.InterpretImage()
        self.CalculateGeometry()
        return self.GenerateMark()
    
if __name__ == '__main__':
    File = "D:\\RepoRoot\\TechDevelopment\\BulkImageProcessor\\InputFolder\\608887.jpg"
    TextConfiguration = {
        "MarkType":"Text",
        "Alignment":{
            "Padding":[200,200,200,200],
            "Vertical":"TOP",
            "Horizontal":"LEFT"
        },
        "ColourMode":"Solid",
        "Colour":[255,255,255],
        "Size":300,
        "Font":"gothamcondensed-book",
        "FontFile":"GothamCondensed-Book.otf",
        "Text":"MagniControlProjects"
    }
    ImageConfiguration = {
        "MarkType":"Image",
        "Alignment":{
            "Padding":[0,0,0,0],
            "Vertical":"TOP",
            "Horizontal":"LEFT"
        },
        "ColourMode":"Solid",
        "Colour":[255,255,255],
        "Scale":1,
        "Path":"D:\\RepoRoot\\TechDevelopment\\simon\\IMG-20220502-WA0009.jpg"
    }
    Masker = WatermarkMasker(
        ImageConfiguration,
        File
        )
    Masker.run(File)
    sys.exit(0)
    