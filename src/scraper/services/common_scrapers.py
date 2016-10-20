import logging
from tornado import ioloop, gen, httpclient

logger = logging.getLogger(__name__)

class CommonScraper(object):
   def __init__(self, name, tcp_server=None):
      self.io_loop = ioloop.IOLoop.instance()
      self.http_client = httpclient.AsyncHTTPClient()
      self.sources = {}
      self.tcp_server = tcp_server
      self.name = name
      self.tcp_server.add_scraper(self)      

   def add_source(self, s):
      self.sources[s.name] = s

   def remove_source(self, name):
      try:
         del self.sources[name]
      except KeyError, e:
         logger.error(e)         
   
   def get_source(self, name):
      try:
         return self.sources[name]
      except KeyError, e:
         raise
