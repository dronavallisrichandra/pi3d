from __future__ import absolute_import, division, print_function, unicode_literals

import Image

from pi3d import *
from pi3d.util import Log

LOGGER = Log.logger(__name__)

def screenshot(filestring):
  """save what in the display to a file
  is will save whatever has been rendered prior to this call since the last
  Display.clear()
  the file will be saved in the top directory if you don't add a path
  """
  from pi3d.Display import DISPLAY
  LOGGER.info('Taking screenshot of "%s"', filestring)

  w, h = DISPLAY.width, DISPLAY.height
  size = h * w * 3
  img = (c_char * size)()
  opengles.glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, ctypes.byref(img))

  im = Image.frombuffer('RGB', (w, h), img, 'raw', 'RGB', 0, 1)
  im = im.transpose(Image.FLIP_TOP_BOTTOM)
  im.save(filestring)

