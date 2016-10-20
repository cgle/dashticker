from tornado import ioloop, gen
import lxml.html
import ujson

def load(name):
   return WEBPAGE_PARSERS[name]

class DefaultParser(object):
   def __init__(self):
      pass
   
class FinvizParser(DefaultParser):
   def __init__(self):
      pass

class SecParser(DefaultParser):
   def __init__(self):
      pass

# init parser instances
WEBPAGE_PARSERS = {
   'default': DefaultParser(),
   'finviz': FinvizParser(),
   'sec': SecParser()
}   

