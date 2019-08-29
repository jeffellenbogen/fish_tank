from time import sleep
import datetime

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
  def __init__(self, filename, rtr, gtr, btr, x_size, y_size):
  
    # top left corner of our image
    self.x = 0
    self.y = 0

    self.x_size = x_size
    self.y_size = y_size

    self.image = Image.open(filename)
    self.image = self.image.convert("RGBA")
    self.image = self.image.resize((x_size,y_size))

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

  ############################################
  # show method 
  #   pastes the icon into the passed image
  ###############################################
  def show(self,image):
    image.paste(self.image,(self.x,self.y),self.mask)

  ############################################
  # move 
  #   Currenly only supports moving right-to-left.
  #   Updates our x and y position to the "next" spot.  
  #   If we go off the screen, we'll reset x, and pick a new
  #     random y.  
  ###############################################
  def move(self, screen_x, screen_y):
    # move one pixel left.
    self.x = self.x - 1
    
    # if we're off the screen, reset to the right, and pick a new y coordinate.
    if (self.x < 0-self.x_size):
      self.x = screen_x
      self.y = random.randint(0,screen_y - self.y_size)

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
      icon.move(self.total_columns, self.total_rows)
      icon.show(self.screen)

    self.screen = self.screen.convert("RGB")
    screen_draw = ImageDraw.Draw(self.screen)

    # draw text on top
    currentDT = datetime.datetime.now()
    time_string = currentDT.strftime("%H:%M:%S")

    # do some math to center our time string
    fnt = ImageFont.truetype("Arial_Bold.ttf",14)
    time_size = fnt.getsize(time_string)
    time_x = (self.total_columns - time_size[0])/2
    time_y = (self.total_rows - time_size[1])/2 
    screen_draw.text((time_x,time_y),time_string, fill = (255,0,0,), font = fnt)

    self.matrix.SetImage(self.screen,0,0)

  
###################################
# Main code 
###################################
matrix_rows = 64
matrix_columns = 64
num_horiz = 1
num_vert = 1

space_tank = Tank(matrix_rows, matrix_columns, num_horiz, num_vert)
space_tank.set_background("andr_small.jpeg")
tie = Icon("tie-fighter-01.jpg",(242,242),(242,242),(242,242),40,40)
space_tank.add_icon(tie)

try:
  print("Press CTRL-C to stop")
  while True:
    space_tank.show()
    sleep(.1)
except KeyboardInterrupt:
  exit(0)
