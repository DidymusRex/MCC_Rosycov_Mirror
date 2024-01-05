"""
https://github.com/GuyCarver/MicroPython/blob/master/esp32/joystick.py
NOTE: For button, Pin 34 didn't work, but pin 32 did.
I don't know what the difference is but not all pins work.
"""
import machine

class Joystick(object) :
  _x_center = 1789.0
  _y_center = 1817.0
  _pos_x = 4095.0 - _x_center
  _pos_y = 4095.0 - _y_center

  def __init__( self, aX, aY, aButton ) :
    self._jx = machine.ADC(machine.Pin(aX))
    self._jy = machine.ADC(machine.Pin(aY))

    #Must be pull up.  Pull down doesn't register change.
    self._js = machine.Pin(aButton, machine.Pin.IN, machine.Pin.PULL_UP)

    self._x = 0.0
    self._y = 0.0
    self._button = False

    self._index = 0
    self._xA = [0, 0, 0]
    self._yA = [0, 0, 0]

  @property
  def x( self ) :
    '''Return value from -1.0 to 1.0.'''
    return self._x

  @property
  def y( self ) :
    '''Return value from -1.0 to 1.0.'''
    return self._y

  @property
  def button( self ) :
    '''return True or False.'''
    return self._button

  def update( self ) :
    self._xA[self._index] = self._jx.read_u16()
    self._yA[self._index] = self._jy.read_u16()

    self._index += 1
    if self._index >= 3 :
      self._index = 0

    rx = float(sum(self._xA)) / 3.0 - self._x_center
    ry = float(sum(self._yA)) / 3.0 - self._y_center
    dx = self._pos_x if rx >= 0 else self._x_center
    dy = self._pos_y if ry >= 0 else self._y_center
    self._x = rx / dx
    self._y = ry / dy

    #Value is 1 when not pressed and 0 when pressed.
    self._button = not self._js.value()
