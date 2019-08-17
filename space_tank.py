# Used in main loop
from time import sleep

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 64 
matrix_columns = 64 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 1 
matrix_vertical = 1

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

#options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

###################################
# Main code 
###################################
icon_size = 40

screen = Image.open("andr_small.jpeg")
screen.convert("RGBA")
screen = screen.resize((total_columns,total_rows))

icon_image = Image.open("tie-fighter-01.jpg")
icon_image = icon_image.convert("RGBA")
icon_image = icon_image.resize((icon_size,icon_size))

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

screen.paste(icon_image,(10,10),mask)
#screen.paste(icon_image,(10,10))

screen = screen.convert("RGB")

matrix.SetImage(screen, 0, 0)

try:
  print("Press CTRL-C to stop")
  while True:
    sleep(100)
except KeyboardInterrupt:
  exit(0)

