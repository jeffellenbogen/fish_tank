from time import sleep
import datetime
from pytz import timezone
import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

###################################
# icon class 
#
#   Icons are the things that move around in the tank.  
#
#   On initialization, you specify an image file, which colors you want as 
#     transparent, and the desired size (in pixels) of that icon.
#
#   The move method updates the image's x and y position.
#  
#   The show method pastes the icon into an image.   
###################################
class Icon():

  ############################################
  # Init method 
  #   rtr, gtr, and btr are the transparency ranges for red, green, and blue 
  #      pixels in our image, represented as a tuple.  Any pixel in that range 
  #      (inclusive) will be marked as transparent.
  ###############################################
  def __init__(self, filename, rtr, gtr, btr, x_size, y_size, total_columns, total_rows):
  
    # top left corner of our image
    self.total_rows = total_rows
    self.total_columns = total_columns

    self.x = total_columns
    self.y = random.randint(0,total_rows - y_size)

    self.x_size = x_size
    self.y_size = y_size

    self.image = Image.open(filename)
    self.image = self.image.convert("RGBA")
    self.image = self.image.resize((x_size,y_size))

    self.slowdown = 1
    self.movecount = 1
    self.direction = 1

    # now that we have our image, we want to make a transparency mask.
    # start by looking at each pixel, and if it's in our transparency 
    # range, make the mask transparent (black).  Otherwise, make it 
    # fully opaque (white)
    self.mask = Image.new("L", (x_size,y_size))
    icon_data = self.image.getdata()
    mask_data = []
    for item in icon_data:
      # uncomment this line if you need to inspect pixels in your image
      # print item

      # is our pixel in range?  
      if ((item[0] >= rtr[0] and item[0] <= rtr[1]) and \
          (item[1] >= gtr[0] and item[1] <= gtr[1]) and \
          (item[2] >= btr[0] and item[2] <= btr[1])):
        mask_data.append(0)
      else:
        mask_data.append(255)
      self.mask.putdata(mask_data)

  ###############################################
  # setSlowdown method 
  ###############################################
  
  def setSlowdown(self,slowdown):
    self.slowdown = slowdown
  
  ###############################################
  # setDirection method 
  ###############################################
  
  def setDirection(self,direction):
    self.direction = direction
  
  ###############################################
  # show method 
  ###############################################
  def show(self,image):
    if self.direction == 1:
      image.paste(self.image,(self.x,self.y),self.mask)
    else:
      tempimage = self.image
      tempimageMask = self.mask
      tempimageFlip = tempimage.transpose(Image.FLIP_LEFT_RIGHT)
      tempimageFlipMask = tempimageMask.transpose(Image.FLIP_LEFT_RIGHT)
      image.paste(tempimageFlip,(self.x,self.y),tempimageFlipMask)


  ############################################
  # move 
  #   Currenly only supports moving right-to-left.
  #   Updates our x and y position to the "next" spot.  
  #   If we go off the screen, we'll reset x, and pick a new
  #     random y.  
  ###############################################
  def move(self):
    if self.movecount < self.slowdown:
      self.movecount += 1
      return
    
    # if we're off the screen, reset to the right, and pick a new y coordinate.
    if ((self.x < 0-self.x_size) or (self.x > self.total_columns)):
      #choose direction
      directionChooser = random.randint(1,11)
      #direction is right
      if directionChooser % 2 == 0: 
        self.direction = 1
        self.x = 0 - self.x_size
      #direction is left  
      else:
        self.direction = -1
        self.x = self.total_columns

      
      if self.y_size >= self.total_rows:
        self.y = random.randint(0,self.total_rows)
      else:
        self.y = random.randint(0,self.total_rows - self.y_size)

    # move one pixel left or right depending on direction. 1 -> Right, -1 -> Left
    self.x = self.x + self.direction
    # increment movecount for slowing down movement if a value is set for .setSlowdown
    self.movecount = 1

###################################
#  Tank class
#
#  A tank has a background image and a list of icons that will be moving 
#  in that tank.
# 
###################################
class Tank():

  ############################################
  # Init method 
  ###############################################
  def __init__(self, panel_rows, panel_columns, num_horiz_panels, num_vert_panels):
 
    self.total_rows = panel_rows * num_vert_panels
    self.total_columns = panel_columns * num_horiz_panels

    options = RGBMatrixOptions()
    options.rows = matrix_rows 
    options.cols = matrix_columns 
    options.chain_length = num_horiz_panels
    options.parallel = num_vert_panels 
    options.hardware_mapping = 'regular' 
    #options.gpio_slowdown = 2

    self.matrix = RGBMatrix(options = options)

    self.background = None
    self.icons = []

    self.screen = Image.new("RGBA",(self.total_columns,self.total_rows))

  ############################################
  # set_background 
  ############################################
  def set_background(self, filename):
    self.background = Image.open(filename)
    self.background.convert("RGBA")
    self.background = self.background.resize((self.total_columns,self.total_rows))
   
  ############################################
  # add_icon 
  ###############################################
  def add_icon(self, icon):
    self.icons.append(icon)

  ############################################
  # show
  #   Displays the whole tank, and then moves any icon elements. 
  ###############################################
  def show(self):
     
    #restore background
    self.screen.paste(self.background,(0,0))
    
    # move and paste in our icons 
    for icon in self.icons:
      icon.move()
      icon.show(self.screen)

    self.screen = self.screen.convert("RGB")
    screen_draw = ImageDraw.Draw(self.screen)


    ################################################
    # Date and time formatting and postioning
    ################################################
    currentDT = datetime.datetime.now()
    time_string = currentDT.strftime("%H:%M:%S")

    #create various fonts
    fnt = ImageFont.truetype("Arial_Bold.ttf",10)
    fnt2 = ImageFont.truetype("Arial_Bold.ttf",12)
    fnt3 = ImageFont.truetype("Arial_Bold.ttf",16)

    #convert to selected timezone and format date/time info
    currentDT = datetime.datetime.now(timezone('UTC'))
    currentDT_TZadjusted = currentDT.astimezone(timezone('US/Mountain'))
    time_string = currentDT_TZadjusted.strftime("%I:%M:%S %p")
    day_of_week = currentDT_TZadjusted.strftime("%A")
    date_string = currentDT_TZadjusted.strftime("%B %d, %Y")
    seconds = int(currentDT_TZadjusted.strftime("%S"))
    
    time_size = fnt2.getsize(time_string)
    day_of_week_size = fnt.getsize(day_of_week)
    date_string_size = fnt.getsize(date_string)

    edge_offset_x = 3
    edge_offset_y = 13
    text_spacing = 4
    
    #draw the text on screen
    screen_draw.text((edge_offset_x,self.total_rows - edge_offset_y * 2),time_string, fill = (255,255,255), font = fnt2)
    screen_draw.text((edge_offset_x, self.total_rows - edge_offset_y),day_of_week, fill = (255,255,255), font = fnt)
    screen_draw.text((edge_offset_x + day_of_week_size[0] + text_spacing, self.total_rows - edge_offset_y),date_string, fill = (255,255,255), font = fnt)

    #special messages here
    specialMessage1 = ("Welcome to")
    specialMessage2 = ("Maker Workshop")
    specialMessage1_size = fnt2.getsize(specialMessage1)
    specialMEssage2_size = fnt3.getsize(specialMessage2)

    screen_draw.text(((self.total_columns - specialMessage1_size[0]) /2,30),specialMessage1, fill = (255,0,0), font = fnt2)
    screen_draw.text(((self.total_columns - specialMessage2_size[0]) /2,70),specialMessage2, fill = (100,0,255), font = fnt)


    #write all changes to the screen
    self.matrix.SetImage(self.screen,0,0)


###################################
# Main code 
###################################
matrix_rows = 32
matrix_columns = 32
num_horiz = 5
num_vert = 3

fish_tank = Tank(matrix_rows, matrix_columns, num_horiz, num_vert)
fish_tank.set_background("images/reef_bgrd_dark_bottom.jpg")
clownfish = Icon("images/clownfish.jpg",(0,10),(200,255),(0,10),40,25,fish_tank.total_columns,fish_tank.total_rows)
clownfish2 = Icon("images/clownfish.jpg",(0,10),(200,255),(0,10),32,20,fish_tank.total_columns,fish_tank.total_rows)
seaTurtle = Icon("images/seaTurtle.jpg",(0,10),(0,10),(150,255),80,50,fish_tank.total_columns,fish_tank.total_rows)
seahorse = Icon("images/seahorse.png",(0,100),(100,255),(0,100),24,32,fish_tank.total_columns,fish_tank.total_rows)
clownfish.setSlowdown(random.randint(0,2))
clownfish2.setSlowdown(random.randint(0,4))
seahorse.setSlowdown(random.randint(0,4))
seaTurtle.setSlowdown(random.randint(0,2))
fish_tank.add_icon(seahorse)
fish_tank.add_icon(clownfish)
fish_tank.add_icon(seaTurtle)
fish_tank.add_icon(clownfish2)

try:
  print("Press CTRL-C to stop")
  while True:
    fish_tank.show()
    sleep(.02)
except KeyboardInterrupt:
  exit(0)
