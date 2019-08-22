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
fnt = ImageFont.truetype("Arial_Bold.ttf",10)
fnt2 = ImageFont.truetype("Arial_Bold.ttf",12)
fnt3 = ImageFont.truetype("Arial_Bold.ttf",16)

clownfish_width = 40
clownfish_height = 25

seaTurtle_width = 80
seaTurtle_height = 50

background = Image.open("reef_bgrd_dark_bottom.jpg")
background.convert("RGBA")
background = background.resize((total_columns,total_rows))

clownfish = Image.open("clownfish_left.jpg")
clownfish = clownfish.convert("RGBA")
clownfish = clownfish.resize((clownfish_width, clownfish_height))

seaTurtle = Image.open("seaTurtle.jpg")
seaTurtle = seaTurtle.convert("RGBA")
seaTurtle = seaTurtle.resize((seaTurtle_width, seaTurtle_height))
seaTurtleStatus = False
seaTurtleSpeed = 2


#####################################################################
# Transparency Masking
# now that we have our image, we want to make a transparency mask.
# start by looking at each pixel, and if it's green (0,255,0), make the mask
# transparent (black).  Otherwise, make it fully opaque (white)
#####################################################################

clownfish_mask = Image.new("L", (clownfish_width,clownfish_height))
clownfish_data = clownfish.getdata()
clownfish_mask_data = []
for item in clownfish_data:
  print item
  if item[0] <= 10 and item[1] >= 245 and item[2] <= 10:
    clownfish_mask_data.append(0)
    print "transparent"
  else:
    clownfish_mask_data.append(255)
    print "opaque"
clownfish_mask.putdata(clownfish_mask_data)
clownfish_x = total_columns
clownfish_y = random.randint(0,total_rows-clownfish_height)

seaTurtle_mask = Image.new("L", (seaTurtle_width,seaTurtle_height))
seaTurtle_data = seaTurtle.getdata()
seaTurtle_mask_data = []
for item in seaTurtle_data:
  print item
  if item[0] <= 30 and item[1] <= 30 and item[2] >= 200:
    seaTurtle_mask_data.append(0)
    print "transparent"
  else:
    seaTurtle_mask_data.append(255)
    print "opaque"
seaTurtle_mask.putdata(seaTurtle_mask_data)
seaTurtle_x = total_columns
seaTurtle_y = random.randint(0,total_rows-seaTurtle_height)



#############################################
# Clownfish direction chooser
#############################################
def clownfishDirectionChooser():
  global clownfish_x
  global clownfish_y
  global total_columns
  global total_rows
  global clownfish_height
  global clownfish_width
  #global clownfish
  #global Image
  #global mask
  
  clownfish_y = random.randint(0,total_rows-clownfish_height)
  clownfish_direction_chooser = random.randint(1,10)
  if clownfish_direction_chooser % 2 == 0:
    clownfish_x = total_columns
    print "swim left"
    return -1
  else: 
    clownfish_x = -clownfish_width
    print "swim right"
    return 1

#############################################
# Main loop
#############################################
screen = Image.new("RGBA",(total_columns,total_rows))
clownfish_direction = clownfishDirectionChooser()

try:
  print("Press CTRL-C to stop")
  while True:

    #restore background (Layer 0)
    screen.paste(background,(0,0))
    
    # paste in our clownfish (Layer 1)
    if clownfish_direction == -1:
      screen.paste(clownfish,(clownfish_x,clownfish_y),clownfish_mask)
    else:
      clownfish_flip = clownfish.transpose(Image.FLIP_LEFT_RIGHT)
      clownfish_flip_mask = clownfish_mask.transpose(Image.FLIP_LEFT_RIGHT)
      screen.paste(clownfish_flip,(clownfish_x,clownfish_y),clownfish_flip_mask)

    # paste in our seaTurtle (Layer 2)
    screen.paste(seaTurtle,(seaTurtle_x, seaTurtle_y), seaTurtle_mask)

    #convert the whole screen from RGBA to RGB so we can display it
    screen = screen.convert("RGB")
    screen_draw = ImageDraw.Draw(screen)

    #########################################
    # draw time information text on top
    #########################################
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

    #(Layer 3 - on top of the image composite called screen)
    screen_draw.text((edge_offset_x,total_rows - edge_offset_y * 2),time_string, fill = (255,255,255), font = fnt2)
    screen_draw.text((edge_offset_x, total_rows - edge_offset_y),day_of_week, fill = (255,255,255), font = fnt)
    screen_draw.text((edge_offset_x + day_of_week_size[0] + text_spacing, total_rows - edge_offset_y),date_string, fill = (255,255,255), font = fnt)
    matrix.SetImage(screen,0,0)

    #########################################
    # Start turtle from right to left at 30 seconds after the minute
    #########################################
    if ((seconds % 30 == 0) & (seaTurtleStatus == False)): 
      print "Seed a turtle now!"
      seaTurtleStatus = True
      seaTurtle_x = -seaTurtle_width
      seaTurtle_y = random.randint(0,total_rows-seaTurtle_height)

    # update our seaTurtle location for next time
    seaTurtle_x = seaTurtle_x + seaTurtleSpeed

    if seaTurtle_x > total_columns:
      seaTurtleStatus = False

    # update our clownfish location for next time
    clownfish_x = clownfish_x + clownfish_direction

    # Moving left, start off screen to the right
    if clownfish_direction == -1:
      if clownfish_x < -clownfish_width:
        clownfish_direction = clownfishDirectionChooser() 
        if clownfish_direction == -1:
          clownfish_x = total_columns
        else: 
          clownfish_x = -clownfish_width
        clownfish_y = random.randint(0,total_rows-clownfish_height)
    # Moving right, start off the screen to the left    
    else:
      if clownfish_x > total_columns:
        clownfish_direction = clownfishDirectionChooser() 
        if clownfish_direction == -1:
          clownfish_x = total_columns
        else: 
          clownfish_x = -clownfish_width
        clownfish_y = random.randint(0,total_rows-clownfish_height)
    sleep(.1)

except KeyboardInterrupt:
  exit(0)

