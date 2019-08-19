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
icon_width = 40
icon_height = 25

fnt = ImageFont.truetype("Arial_Bold.ttf",10)
fnt2 = ImageFont.truetype("Arial_Bold.ttf",12)
fnt3 = ImageFont.truetype("Arial_Bold.ttf",16)


background = Image.open("reef_bgrd_dark_bottom.jpg")
background.convert("RGBA")
background = background.resize((total_columns,total_rows))




icon_image = Image.open("clownfish_left.jpg")
icon_image = icon_image.convert("RGBA")
icon_image = icon_image.resize((icon_width, icon_height))

# now that we have our image, we want to make a transparency mask.
# start by looking at each pixel, and if it's green, make the mask
# transparent (black).  Otherwise, make it fully opaque (white)

mask = Image.new("L", (icon_width,icon_height))
icon_data = icon_image.getdata()
mask_data = []
for item in icon_data:
  print item
  if item[0] <= 10 and item[1] >= 245 and item[2] <= 10:
    mask_data.append(0)
    print "transparent"
  else:
    mask_data.append(255)
    print "opaque"
mask.putdata(mask_data)

icon_x = total_columns
icon_y = random.randint(0,total_rows-icon_height)

screen = Image.new("RGBA",(total_columns,total_rows))


#############################################
# Clownfish direction chooser
#############################################
def clownfishDirectionChooser():
  global icon_x
  global icon_y
  global total_columns
  global total_rows
  global icon_height
  global icon_width
  global icon_image
  global Image

  clownfish_direction_chooser = random.randint(1,10)
  if clownfish_direction_chooser % 2 == 0:
    icon_x = total_columns
    icon_y = random.randint(0,total_rows-icon_height)
    icon_image = Image.open("clownfish_left.jpg")
    icon_image = icon_image.convert("RGBA")
    icon_image = icon_image.resize((icon_width, icon_height))

    mask = Image.new("L", (icon_width,icon_height))
    icon_data = icon_image.getdata()
    mask_data = []
    for item in icon_data:
      print item
      if item[0] <= 10 and item[1] >= 245 and item[2] <= 10:
        mask_data.append(0)
        print "transparent"
      else:
        mask_data.append(255)
        print "opaque"
    mask.putdata(mask_data)
    print "swim left"
    return -1
  else: 
    icon_x = -icon_width
    icon_y = random.randint(0,total_rows-icon_height)
    icon_image = Image.open("clownfish_right.jpg")
    icon_image = icon_image.convert("RGBA")
    icon_image = icon_image.resize((icon_width, icon_height))

    mask = Image.new("R", (icon_width,icon_height))
    icon_data = icon_image.getdata()
    mask_data = []
    for item in icon_data:
      print item
      if item[0] <= 10 and item[1] >= 245 and item[2] <= 10:
        mask_data.append(0)
        print "transparent"
      else:
        mask_data.append(255)
        print "opaque"
    mask.putdata(mask_data)
    print "swim right"
    return 1

#############################################
# Main loop
#############################################
clownfish_direction = clownfishDirectionChooser()
try:
  print("Press CTRL-C to stop")
  while True:

    #restore background
    screen.paste(background,(0,0))
    
    # paste in our ship
    screen.paste(icon_image,(icon_x,icon_y),mask)


    screen = screen.convert("RGB")
    screen_draw = ImageDraw.Draw(screen)

    # draw text on top
    currentDT = datetime.datetime.now(timezone('UTC'))
    currentDT_TZadjusted = currentDT.astimezone(timezone('US/Mountain'))
    time_string = currentDT_TZadjusted.strftime("%I:%M:%S %p")
    day_of_week = currentDT_TZadjusted.strftime("%A")
    date_string = currentDT_TZadjusted.strftime("%B %d, %Y")


    time_size = fnt2.getsize(time_string)
    day_of_week_size = fnt.getsize(day_of_week)
    date_string_size = fnt.getsize(date_string)

    edge_offset_x = 3
    edge_offset_y = 13
    text_spacing = 4

    screen_draw.text((edge_offset_x,total_rows - edge_offset_y * 2),time_string, fill = (255,255,255), font = fnt2)
    screen_draw.text((edge_offset_x, total_rows - edge_offset_y),day_of_week, fill = (255,255,255), font = fnt)
    screen_draw.text((edge_offset_x + day_of_week_size[0] + text_spacing, total_rows - edge_offset_y),date_string, fill = (255,255,255), font = fnt)
    matrix.SetImage(screen,0,0)


    # update our location for next time
    icon_x = icon_x + clownfish_direction
    if clownfish_direction == -1:
      if icon_x < (0 - icon_width):
        clownfish_direction = clownfishDirectionChooser() 
        if clownfish_direction == -1:
          icon_x = total_columns
        else: 
          icon_x = -icon_width
        icon_y = random.randint(0,total_rows-icon_height)
    else:
      if icon_x > total_columns + icon_width:
        clownfish_direction = clownfishDirectionChooser() 
        if clownfish_direction == -1:
          icon_x = total_columns
        else: 
          icon_x = icon_width
        icon_y = random.randint(0,total_rows-icon_height)
    sleep(.1)

except KeyboardInterrupt:
  exit(0)

