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
        
    def ChangeInputImage(
            self,
            NewInputImage
            ):
        '''
        After the object has been constructed, if the configuration remains the same, just the 
        image path may be used and the process can be re-run.
        '''
        self.InputImage = NewInputImage
    
    def InterpretConfiguration(self):
        '''
        Where MarkType is Text, we expect:
        - "Font": name of the font to be used"
        - "FontFile": relative path to the font file.
        - "Text": String of letters to place on the artwork.
        
        Where MarkType is "Image", we expect:
        - "Path": to point at the image file absolute path.
        - "Scale": Currently scales the watermark by a factor. TODO: Make description of how to scale.
        - "Background": For non RGBa format files, describes the colour used for the background.
        
        Both:
        - "GenerateMask" 
        '''
        self.AlignmentX = self.Configuration["Alignment"]["Horizontal"]
        self.AlignmentY = self.Configuration["Alignment"]["Vertical"]
        try:
            self.PadX = self.Configuration["Alignment"]["PadX"]
        except:
            self.PadX = 0
        try:
            self.PadY = self.Configuration["Alignment"]["PadY"]
        except:
            self.PadY = 0
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
            try:
                self.Background = self.Configuration["Background"]
            except:
                self.Background = "Transparent"
            #self.PreserveColours = self.Configuration["PreserveColours"]
        try:
            self.GenerateMask = self.Configuration["GenerateMask"]
        except:
            self.GenerateMask = False
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
            self.ImageType = I_Image.mode
        print(f"Image is w:{self.ImageWidth}px h:{self.ImageHeight}px")
        print(f"Image type is {self.ImageType}")
        return
        
    def CalculateGeometry(self):
        '''
        Workout where the text is going to land. Using Adobe definition for alignment.
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
            self.DrawX = self.ImageWidth - self.MarkWidth - self.PadX
        elif self.AlignmentX.upper() == "LEFT":
            print ("Aligning Y Left")
            self.DrawX = 0 + self.PadX
            
        #Determine Y Draw Position
        if self.AlignmentY.upper() == "MIDDLE" or self.AlignmentY.upper() == "CENTER":
            print ("Aligning Y Centre")
            self.DrawY = (self.ImageHeight/2) - (self.MarkHeight/2)
        elif self.AlignmentY.upper() == "BOTTOM":
            print ("Aligning Y Bottom")
            self.DrawY = self.ImageHeight - self.MarkHeight - self.PadY
        elif self.AlignmentY.upper() == "TOP":
            print ("Aligning Y Bottom")
            self.DrawY = 0 + self.PadY
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
            if MaskInput.mode == "RGB":
                if self.Background == "Black":
                    for px_X in range(MaskInput.width):
                        for px_Y in range(MaskInput.height):
                                Pixel = MaskInput.getpixel((px_X,px_Y))
                                if Pixel[0] > 35 or Pixel[1] > 35 or Pixel[2] > 35: #Check > 50 for aliasing.
                                    Drawable.point((px_X,px_Y),fill=0)
                                    DrawOut.point((px_X+self.DrawX,px_Y+self.DrawY),Pixel)
                elif self.Background == "White":
                    for px_X in range(MaskInput.width):
                        for px_Y in range(MaskInput.height):
                                Pixel = MaskInput.getpixel((px_X,px_Y))
                                if Pixel[0] < 220  or Pixel[1] < 220 or Pixel[2] < 220: #Check > 50 for aliasing.
                                    Drawable.point((px_X,px_Y),fill=0)
                                    DrawOut.point((px_X+self.DrawX,px_Y+self.DrawY),Pixel)
            else:
                #being lazy assuming catchall for transparent.
                for px_X in range(MaskInput.width):
                    for px_Y in range(MaskInput.height):
                            Pixel = MaskInput.getpixel((px_X,px_Y))
                            if Pixel[3] > 20:
                                Drawable.point((px_X,px_Y),fill=0)
                                DrawOut.point((px_X+self.DrawX,px_Y+self.DrawY),fill=(Pixel[0],Pixel[1],Pixel[2]))
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
    