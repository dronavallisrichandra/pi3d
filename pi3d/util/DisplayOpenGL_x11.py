import ctypes

from ctypes import c_int, c_float

from pi3d.constants import *

from pi3d.util.Ctypes import c_ints

from pyxlib import xlib
from pyxlib.x import *

class DisplayOpenGL(object):
  def __init__(self):
    self.d = xlib.XOpenDisplay(None)
    self.screen = xlib.XDefaultScreenOfDisplay(self.d)
    self.width, self.height = xlib.XWidthOfScreen(self.screen), xlib.XHeightOfScreen(self.screen)

  def create_display(self, x=0, y=0, w=0, h=0, depth=24):
    self.display = openegl.eglGetDisplay(EGL_DEFAULT_DISPLAY)
    assert self.display != EGL_NO_DISPLAY

    r = openegl.eglInitialize(self.display, 0, 0)
    #assert r == EGL_FALSE

    attribute_list = c_ints((EGL_RED_SIZE, 8,
                             EGL_GREEN_SIZE, 8,
                             EGL_BLUE_SIZE, 8,
                             EGL_DEPTH_SIZE, depth,
                             EGL_ALPHA_SIZE, 8,
                             EGL_BUFFER_SIZE, 32,
                             EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
                             EGL_NONE))
    numconfig = c_int()
    self.config = ctypes.c_void_p()
    r = openegl.eglChooseConfig(self.display,
                                ctypes.byref(attribute_list),
                                ctypes.byref(self.config), 1,
                                ctypes.byref(numconfig))

    context_attribs = c_ints((EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE))
    self.context = openegl.eglCreateContext(self.display, self.config,
                                            EGL_NO_CONTEXT, ctypes.byref(context_attribs) )
    assert self.context != EGL_NO_CONTEXT

    self.create_surface(x, y, w, h)

    opengles.glDepthRangef(c_float(-1.0), c_float(1.0))
    opengles.glClearColor (c_float(0.3), c_float(0.3), c_float(0.7), c_float(1.0))
    opengles.glBindFramebuffer(GL_FRAMEBUFFER, 0)

    #Setup default hints
    opengles.glEnable(GL_CULL_FACE)
    opengles.glEnable(GL_NORMALIZE)
    opengles.glEnable(GL_DEPTH_TEST)
    opengles.glCullFace(GL_FRONT)
    opengles.glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST)

    # Switches off alpha blending problem with desktop - is there a bug in the
    # driver?
    # Thanks to Roland Humphries who sorted this one!!
    opengles.glColorMask(1, 1, 1, 0)

    #opengles.glEnableClientState(GL_VERTEX_ARRAY)
    #opengles.glEnableClientState(GL_NORMAL_ARRAY)
    self.active = True

  def create_surface(self, x=0, y=0, w=0, h=0):
    #Set the viewport position and size
    dst_rect = c_ints((x, y, w, h))
    src_rect = c_ints((x, y, w << 16, h << 16))

    self.width, self.height = w, h

    # Set some WM info
    root = xlib.XRootWindowOfScreen(self.screen)
    self.window = xlib.XCreateSimpleWindow(self.d, root, x, y, w, h, 1, 0, 0)

    s = ctypes.create_string_buffer(b'WM_DELETE_WINDOW')
    self.WM_DELETE_WINDOW = ctypes.c_ulong(xlib.XInternAtom(self.d, s, 0))
    #TODO add functions to xlib for these window manager libx11 functions
    #self.window.set_wm_name('pi3d xlib window')
    #self.window.set_wm_icon_name('pi3d')
    #self.window.set_wm_class('draw', 'XlibExample')

    xlib.XSetWMProtocols(self.d, self.window, ctypes.byref(self.WM_DELETE_WINDOW), 1)
    #self.window.set_wm_hints(flags = Xutil.StateHint,
    #                         initial_state = Xutil.NormalState)

    #self.window.set_wm_normal_hints(flags = (Xutil.PPosition | Xutil.PSize
    #                                         | Xutil.PMinSize),
    #                                min_width = 20,
    #                                min_height = 20)
    
    xlib.XSelectInput(self.d, self.window, KeyPressMask)
    xlib.XMapWindow(self.d, self.window)
    self.surface = openegl.eglCreateWindowSurface(self.display, self.config, self.window, 0)

    assert self.surface != EGL_NO_SURFACE

    r = openegl.eglMakeCurrent(self.display, self.surface, self.surface,
                               self.context)
    assert r

    #Create viewport
    opengles.glViewport(0, 0, w, h)

  def resize(self, x=0, y=0, w=0, h=0):
    # Destroy current surface and native window
    openegl.eglSwapBuffers(self.display, self.surface)
    #openegl.eglDestroySurface(self.display, self.surface)

    #self.dispman_update = bcm.vc_dispmanx_update_start(0)
    #bcm.vc_dispmanx_element_remove(self.dispman_update,
    #                               self.dispman_element)
    #bcm.vc_dispmanx_update_submit_sync(self.dispman_update)
    #bcm.vc_dispmanx_display_close(self.dispman_display)

    #Now recreate the native window and surface
    #self.create_surface(x, y, w, h)


  def destroy(self, display=None):
    if self.active:
      ###### brute force tidying experiment TODO find nicer way ########
      if display:
        func_list = [[opengles.glIsBuffer, opengles.glDeleteBuffers,
            dict(display.vbufs_dict.items() + display.ebufs_dict.items())],
            [opengles.glIsTexture, opengles.glDeleteTextures,
            display.textures_dict],
            [opengles.glIsProgram, opengles.glDeleteProgram, 0],
            [opengles.glIsShader, opengles.glDeleteShader, 0]]
        i_ct = (ctypes.c_int * 1)(0) #convoluted 0
        for func in func_list:
          max_streak = 100
          streak_start = 0
          if func[2]: # list to work through
            for i in func[2]:
              if func[0](func[2][i][0]) == 1: #check if i exists as a name
                func[1](1, ctypes.byref(func[2][i][0]))
          else: # just do sequential numbers
            for i in xrange(10000):
              if func[0](i) == 1: #check if i exists as a name
                i_ct[0] = i #convoluted 1
                func[1](ctypes.byref(i_ct))
                streak_start = i
              elif i > (streak_start + 100):
                break
      ##################################################################
      openegl.eglSwapBuffers(self.display, self.surface)
      openegl.eglMakeCurrent(self.display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                             EGL_NO_CONTEXT)
      openegl.eglDestroySurface(self.display, self.surface)
      openegl.eglDestroyContext(self.display, self.context)
      openegl.eglTerminate(self.display)

      self.active = False
      xlib.XCloseDisplay(self.d)
      #sys.exit(0)

  def swap_buffers(self):
    #opengles.glFlush()
    #opengles.glFinish()
    #clear_matrices
    openegl.eglSwapBuffers(self.display, self.surface)
