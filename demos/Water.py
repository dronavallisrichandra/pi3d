from __future__ import absolute_import

import math, random, time, glob

import demo
demo.demo(__name__)

from pi3d import *

from pi3d import Display
from pi3d.Texture import Texture
from pi3d.Keyboard import Keyboard

from pi3d.context.Light import Light
from pi3d.Shader import Shader

from pi3d.shape.Sphere import Sphere
from pi3d.util.String import String
from pi3d.util.Ttffont import Ttffont
from pi3d.shape.MergeShape import MergeShape
from pi3d.shape.Plane import Plane
from pi3d.util.Screenshot import screenshot

print "====================================================="
print "press escape to escape"
print "move this terminal window to top of screen to see FPS"
print "====================================================="

# Setup display and initialise pi3d
DISPLAY = Display.create(x=200, y=150)
DISPLAY.set_background(0.4, 0.6, 0.8, 0.5)      # r,g,b,alpha

#setup textures, light position and initial model position
Light((5, -5, 8))
#create shaders
shader = Shader("shaders/uv_reflect")
matsh = Shader("shaders/mat_reflect")
flatsh = Shader("shaders/uv_flat")

#Create textures
shapeimg = Texture("textures/straw1.jpg")
shapebump = Texture("textures/mudnormal.jpg")
waterbump = []
iFiles = glob.glob("textures/water/n_norm0??.png")
iFiles.sort() # order is vital to animation!
for f in iFiles:
  waterbump.append(Texture(f))
num_n = len(waterbump)
shapeshine = Texture("textures/stars.jpg")

#Create shape
myshape = MergeShape()
num = (2, 2)
asphere = Sphere(sides=32)
for i in range(num[0]):
  for j in range(num[1]):
    myshape.add(asphere, -num[0]*0.9 + 1.8*i, -num[1]*0.9 +1.8*j, 0.0)

myshape.position(0.0, 0.0, 5)
myshape.set_draw_details(shader, [shapeimg, shapebump, shapeshine], 1.0, 0.1)
myshape.set_material((1.0, 0.5, 0.2, 0.5))

mywater = Plane(w=100.0, h=100.0)
mywater.set_draw_details(matsh, [waterbump[0], shapeshine], 8.0, 0.6)
mywater.set_material((0.0, 0.05, 0.1))
mywater.set_fog((0.4, 0.6, 0.8, 0.0),150)
mywater.rotateToX(90)
mywater.position(0.0, -2.0, 50.0)

arialFont = Ttffont("fonts/FreeMonoBoldOblique.ttf", "#dd00aa")   #load ttf font and set the font colour to 'raspberry'
mystring = String(font=arialFont, string="Now the Raspberry Pi really does rock")
mystring.translate(0.0, 0.0, 1)
mystring.set_shader(flatsh)

tick = 0
av_fps = 0
i_n=0
spf = 0.05
next_time = time.time() + spf
dx = 0.02

# Fetch key presses.
mykeys = Keyboard()
fr = 0
# Display scene and rotate shape
while DISPLAY.loop_running():

  myshape.draw()
  myshape.rotateIncY(0.247)
  myshape.rotateIncZ(0.1613)
  myshape.translateX(dx)
  if myshape.x() > 5: dx = -0.05
  elif myshape.x() < -5: dx = 0.05

  mywater.draw()

  mystring.draw()
  mystring.rotateIncZ(0.05)

  if time.time() > next_time:
    i_n = (i_n + 1) % num_n
    mywater.buf[0].textures[0] = waterbump[i_n]
    next_time = time.time() + spf
    av_fps = av_fps*0.9 + tick/spf*0.1 # exp smooth moving average
    print av_fps,"FPS"
    tick = 0

  tick += 1

  #screenshot("/media/E856-DA25/New/fr%03d.jpg" % fr)
  #fr += 1

  if mykeys.read() == 27:
    mykeys.close()
    DISPLAY.destroy()
    break


quit()
