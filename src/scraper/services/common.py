import logging, functools
import datetime, time, ujson, lxml
from tornado import ioloop, gen, httpclient, netutil
import socket

logger = logging.getLogger(__name__)

class CommonSource(object):
   source_type = None

   def __init__(self, name=None, description=None, url_pattern=None,
                      req_timeout=5, conn_timeout=5, proxy=(None,None),
                      default_interval=5, start_time=None, stop_time=None, 
                      io_loop=None, http_client=None):

      self._req_timeout = req_timeout
      self._conn_timeout = conn_timeout
      self._proxy = proxy

      self._default_interval = datetime.timedelta(seconds=5)
      self._start_time = start_time
      self._stop_time = stop_time

      self._timers = {} # url => timer

      self.io_loop = io_loop      
      self.http_client = httpclient.AsyncHTTPClient(io_loop=io_loop) \
                         if http_client is None else http_client

      self.name = name
      self.description = description
      self.url_pattern = url_pattern
      
   @gen.coroutine
   def fetch(self, url=None, **kwargs):
      # get url
      url = url if url else self.get_url(**kwargs)
      logger.debug('FETCHING {}'.format(url))
      response = None
      try:
         proxy_host, proxy_port = self._proxy
         req = httpclient.HTTPRequest(url,
                                      method='GET',
                                      connect_timeout=self._conn_timeout,
                                      request_timeout=self._req_timeout,
                                      proxy_host=proxy_host,
                                      proxy_port=proxy_port)

         response = yield self.http_client.fetch(req)
      except httpclient.HTTPError as e:
         logger.error('FETCH URL HTTPERROR: {}'.format(e))
      except Exception, e:
         logger.error('FETCH URL ERROR: {}'.format(e))
      
      raise gen.Return(response)
   
   def parse(self, raw_data):
      raise NotImplementedError

   def query(self, cmd):
      raise NotImplementedError

   def get_url(self, **kwargs):
      return self.url_pattern.format(**kwargs)

   @classmethod
   def load_from_spec(cls, spec):
      raise NotImplementedError
   
   @gen.coroutine
   def _default_timer_callback(self, url):
      response = yield self.fetch(url=url)
      #if response is not None:
         #logger.debug('FETCHED: {}'.format(response.body))
         
      raise gen.Return(response)
   
   @gen.coroutine  
   def _handle_on_timer(self, interval, url, timer_callback=None):
      try:
         out = yield timer_callback()
      except TypeError:
         out = yield self._default_timer_callback(url)
      
      self._timers[url] = self.io_loop.add_timeout(interval, self._handle_on_timer, 
                                                   interval, url, timer_callback=timer_callback)

   # timer for specific url
   # default 5 secs
   def start_timer(self, url=None, interval=None, timer_callback=None,):
      if url in self._timers:
         logger.debug('{} timer already running'.format(url))
         return
      
      logger.debug('starting timer for {}'.format(url))
      interval = interval if interval else self._default_interval
      self._timers[url] = self.io_loop.add_timeout(interval, self._handle_on_timer, 
                                                   interval, url, timer_callback=timer_callback)

   def stop_timer(self, url):
      if url not in self._timers:
         return

      logger.debug('stopping timer for {}'.format(url))
      self.io_loop.remove_timeout(self._timers[url])
      del self._timers[url]

   def get_all_timer_urls(self):
      return self._timers.keys()
   
   def get_timer(self, url):
      try:
         return self._timers[url]
      except KeyError:
         raise RuntimeError('url {} not found in timer'.format(url))

class JSONSource(CommonSource):
   def __init__(self, **kwargs):
      super(JSONSource, self).__init__(**kwargs)

   @classmethod
   def load_from_spec(cls, spec):
      pass

   def parse(self, raw_data):
      pass

   def query(self, cmd):
      pass
   

class XMLSource(CommonSource):
   def __init__(self):
      pass
   
   @classmethod
   def load_from_spec(cls, spec):
      pass

   def parse(self, raw_data):
      pass

   def query(self, cmd):
      pass
   


class WebpageSource(CommonSource):
   def __init__(self):
      pass
   
   @classmethod
   def load_from_spec(cls, spec):
      pass

   def parse(self, raw_data):
      pass

   def query(self, cmd):
      pass
   


class CommonScraper(object):
   def __init__(self, port):
      self.io_loop = ioloop.IOLoop.instance()
      self.http_client = httpclient.AsyncHTTPClient()
      
      self.sources = {}
      self.sock = None

   def add_source(self, spec):
      pass
