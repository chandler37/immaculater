from icecream import ic

ic.configureOutput(includeContext=True)

try:
    builtins = __import__('__builtin__')
except ImportError:
    builtins = __import__('builtins')

setattr(builtins, 'ic', ic)
