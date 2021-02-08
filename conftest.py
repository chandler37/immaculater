import icecream
import os


_MARKER = os.environ.get('IC_MARKER', 'D' 'LC')

icecream.ic = icecream.IceCreamDebugger(prefix=f"\n{_MARKER} ic|", outputFunction=icecream.stderrPrint)  # no colorization
icecream.ic.configureOutput(includeContext=os.environ.get('IC') != '0')

try:
  builtins = __import__('__builtin__')
except ImportError:
  builtins = __import__('builtins')

setattr(builtins, _MARKER, icecream.ic)
