from time import sleep
import datetime
from pytz import timezone


import random

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

# this is the size of ONE of our matrixes. 
matrix_rows = 32
matrix_columns = 32 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 5 
matrix_vertical = 3

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 
#options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.hardware_mapping = 'regular' 

options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

###################################
# Main code 
###################################


fnt = ImageFont.truetype("Arial_Bold.ttf",14)
fnt2 = ImageFont.truetype("Arial_Bold.ttf",20)
fnt3 = ImageFont.truetype("Arial_Bold.ttf",16)


background = Image.open("images/andr_small.jpeg")
background.convert("RGBA")
background = background.resize((total_columns,total_rows))

icon_size = 40
icon_image = Image.open("images/tie-fighter-01.jpg")
icon_image = icon_image.convert("RGBA")
icon_image = icon_image.resize((icon_size,icon_size))
icon_x = total_columns
icon_y = random.randint(0,total_rows-icon_size)

falcon_imageWidth = 102
falcon_imageHeight = 50
falcon_image = Image.open("images/Millennium-Falcon.png")
falcon_image = falcon_image.convert("RGBA")
falcon_image = falcon_image.resize((falcon_imageWidth,falcon_imageHeight))
falcon_x = - falcon_imageWidth
falcon_y = random.randint(0,total_rows - falcon_imageHeight)

# now that we have our image, we want to make a transparency mask.
# start by looking at each pixel, and if it's white, make the mask
# transparent (black).  Otherwise, make it fully opaque (white)
# Note that further inspection of our image shows that the background isn't 
# a full 255,255,255...it's 242,242,242.
mask = Image.new("L", (icon_size,icon_size))
icon_data = icon_image.getdata()
mask_data = []
for item in icon_data:
  print item
  if item[0] == 242 and item[1] == 242 and item[2] == 242:
    mask_data.append(0)
    print "transparent"
  else:
    mask_data.append(255)
    print "opaque"
mask.putdata(mask_data)

falcon_mask = Image.new("L", (falcon_imageWidth,falcon_imageHeight))
falcon_data = falcon_image.getdata()
falcon_mask_data = []
for item in falcon_data:
  print item
  if item[0] >= 120 and item[1] <= 60 and item[2] <= 60:
    falcon_mask_data.append(0)
    print "transparent"
  else:
    falcon_mask_data.append(255)
    print "opaque"
falcon_mask.putdata(falcon_mask_data)

screen = Image.new("RGBA",(total_columns,total_rows))

try:
  print("Press CTRL-C to stop")
  while True:

    #restore background
    screen.paste(background,(0,0))
    
    # paste in our tie-fighter
    screen.paste(icon_image,(icon_x,icon_y),mask)

    # paste in our millinium falcon
    screen.paste(falcon_image,(falcon_x,falcon_y),falcon_mask)

    screen = screen.convert("RGB")
    screen_draw = ImageDraw.Draw(screen)

    # draw text on top
    currentDT = datetime.datetime.now(timezone('UTC'))
    currentDT_TZadjusted = currentDT.astimezone(timezone('US/Mountain'))
    time_string = currentDT_TZadjusted.strftime("%I:%M:%S %p")
    day_of_week = currentDT_TZadjusted.strftime("%A")
    date_string = currentDT_TZadjusted.strftime("%B %d, %Y")

    # do some math to center our time string
    time_size = fnt.getsize(time_string)
    day_of_week_size = fnt2.getsize(day_of_week)
    date_string_size = fnt3.getsize(date_string)

    time_x = (total_columns - time_size[0])/2
    time_y = (total_rows - time_size[1])/2 
    
    day_x = (total_columns - day_of_week_size[0])/2
    day_vertical_offset = -40
    day_y = time_y + day_vertical_offset

    date_x = (total_columns - date_string_size[0])/2
    date_vertical_offset = -17
    date_y = time_y + date_vertical_offset

    screen_draw.text((time_x,time_y),time_string, fill = (219,4,216), font = fnt)
    screen_draw.text((day_x, day_y),day_of_week, fill = (255,255,255), font = fnt2)
    screen_draw.text((date_x, date_y),date_string, fill = (245,245,66), font = fnt3)
    matrix.SetImage(screen,0,0)

    # update our location for next time
    icon_x = icon_x - 1
    if (icon_x < (0 - icon_size)):
      icon_x = total_columns
      icon_y = random.randint(0,total_rows-icon_size)


    falcon_x = falcon_x + (1/4)
    if falcon_x % 1 == 0:
      if (falcon_x > total_columns):
        falcon_x = -3 * total_columns
        falcon_y = random.randint(0,total_rows - falcon_imageHeight)

    sleep(.1)

except KeyboardInterrupt:
  exit(0)

