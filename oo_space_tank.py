from time import sleep
import datetime

import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont


class Icon():
    """Icons are the things that move around in the tank

    On initialization, you specify an image file, which colors you want as transparent, and the desired size
    (in pixels) of that icon.

    Parameters
    ----------
    filename : str
        Location of the icon image file
    rtr : tuple
        A transparency range for red in which any pixel in that range will be marked as transparent
    gtr : tuple
        A transparency range for green in which any pixel in that range will be marked as transparent
    btr : tuple
        A transparency range for blue in which any pixel in that range will be marked as transparent
    x_size : int
    y_size : int
    total_columns : int
    total_rows : int

    Returns
    -------
    oo_space_tank.Icon class

    """

    def __init__(self, filename, rtr, gtr, btr, x_size, y_size, total_columns, total_rows, **kwargs):

        self.total_rows = total_rows
        self.total_columns = total_columns
        self.x = total_columns + random.randint(0, 30)
        self.y = random.randint(0, total_rows)
        self.x_size = x_size
        self.y_size = y_size
        self.image = self.get_image(filename)
        self.image_data = self.image.getdata()
        self.mask = self.get_mask()

        # use kwargs to set a default value but still allow users to change it by passing keyword args to the Class()
        self.slowdown = kwargs.get('slowdown', 1)
        self.movecount = kwargs.get('movecount', 1)

        self.put_mask_data()

    def set_slowdown(self, slowdown):
        setattr(self, 'slowdown', slowdown)

    def get_mask(self):
        return Image.new("L", (self.x_size, self.y_size))

    def get_image(self, filename):
        _img = Image.open(filename)
        _img = _img.convert("RGBA")
        _img = _img.resize((self.x_size, self.y_size))
        return _img

    def put_mask_data(self):
        """Make a transparency mask. Inspect rgb ranges and make transparent (in range) or opaque (not in range).
        """
        _mask_data = []

        for item in self.icon_data:
            if (item[0] >= self.rtr[0] and item[0] <= self.rtr[1] and
                    item[1] >= self.gtr[0] and item[1] <= self.gtr[1] and
                    item[2] >= self.btr[0] and item[2] <= self.btr[1]):
                _mask_data.append(0)
            else:
                _mask_data.append(255)
            self.mask.putdata(_mask_data)

    def show(self, image):
        """Pastes the icon into the passed image.
        """
        image.paste(self.image, (self.x, self.y), self.mask)

    def move(self):
        if self.movecount < self.slowdown:
            self.movecount += 1
            return

        # move one pixel left.
        self.x = self.x - 1
        self.movecount = 1

        # if we're off the screen, reset to the right, and pick a new y coordinate.
        if (self.x < 0-self.x_size):
            self.x = self.total_columns + random.randint(0, 50)
        if self.y_size >= self.total_rows:
            self.y = random.randint(0, self.total_rows)
        else:
            self.y = random.randint(0, self.total_rows - self.y_size)


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

    # this pattern of instantiating (creating) objects if called "keyword args" or "kwargs"
    options_dict = {
        'rows': matrix_rows,
        'cols': matrix_columns,
        'chain_length': num_horiz_panels,
        'parallel': num_vert_panels,
        'hardware_mapping': 'regular'
    }
    self.options = RGBMatrixOptions(**options_dict)
    self.matrix = RGBMatrix(options=self.options)

    self.background = None
    self.icons = []

    self.screen = Image.new("RGBA", (self.total_columns, self.total_rows))

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
matrix_rows = 32
matrix_columns = 32
num_horiz = 5
num_vert = 3

space_tank = Tank(matrix_rows, matrix_columns, num_horiz, num_vert)
space_tank.set_background("images/andr_small.jpeg")
tie = Icon("images/tie-fighter-01.jpg",(242,242),(242,242),(242,242),40,40,space_tank.total_columns,space_tank.total_rows)
fish = Icon("images/clownfish_left.jpg",(0,10),(200,255),(0,10),40,25,space_tank.total_columns,space_tank.total_rows)
fish.setSlowdown(3)
space_tank.add_icon(tie)
space_tank.add_icon(fish)

try:
  print("Press CTRL-C to stop")
  while True:
    space_tank.show()
    sleep(.025)
except KeyboardInterrupt:
  exit(0)
