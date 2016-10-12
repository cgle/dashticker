import logging, functools
import datetime, time, ujson, lxml, re
from tornado import ioloop, gen, httpclient, netutil
import socket
import uuid

logger = logging.getLogger(__name__)

class CommonSource(object):
   _source_type = None
   def __init__(self, name=None, description=None, url_pattern=None,
                      req_timeout=None, conn_timeout=None, proxy=None,
                      start_time=None, stop_time=None, io_loop=None, http_client=None):

      self._req_timeout = req_timeout if req_timeout else 5
      self._conn_timeout = conn_timeout if conn_timeout else 5
      # TODO: randomize proxy
      self._proxy = proxy

      self._default_interval = datetime.timedelta(seconds=15)
      self._start_time = start_time
      self._stop_time = stop_time

      self._timers = {} # url => timer

      self.io_loop = io_loop      
      self.http_client = httpclient.AsyncHTTPClient(io_loop=io_loop) \
                         if http_client is None else http_client

      self.name = name
      self.description = description
      self.url_pattern = url_pattern

   @classmethod
   def load_from_spec(cls, *args, **kwargs):
      raise NotImplementedError

   @gen.coroutine
   def fetch(self, url=None, **kwargs):
      # get url
      url = url if url else self.get_url(**kwargs)
      logger.debug('FETCHING {}'.format(url))
      response = None
      try:
         proxy_host = self._proxy['host'] if self._proxy else None
         proxy_port = self._proxy['port'] if self._proxy else None
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
   
   def source_type(self):
      return self._source_type

   def parse(self, raw_data):
      raise NotImplementedError

   def query(self, cmd):
      raise NotImplementedError

   def get_url(self, **kwargs):
      return self.url_pattern.format(**kwargs)
   
   @gen.coroutine
   def _default_timer_callback(self, url):
      response = yield self.fetch(url=url)
      if response is not None:
         logger.debug('FETCHED: {}'.format(response.body))
         
      raise gen.Return(response)
   
   @gen.coroutine  
   def _handle_on_timer(self, interval, url, timer_callback=None):
      try:
         out = yield timer_callback()
      except TypeError:
         out = yield self._default_timer_callback(url)
      
      self._timers[url] = self.io_loop.add_timeout(interval, self._handle_on_timer, 
                                                   interval, url, timer_callback=timer_callback)

   def start_timer(self, url=None, url_args=None, interval=None, timer_callback=None,):
      url = url if url else self.get_url(**url_args)

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
   _source_type = 'json'
   _json_start_regex = re.compile('\{|\[')

   def __init__(self, data_fields, **kwargs):
      super(JSONSource, self).__init__(**kwargs)      
      self._data_fields = data_fields

   @classmethod
   def load_from_spec(cls, spec, io_loop=None, http_client=None):
      logging.debug('loading new JSONSource object from spec')
      try:
         data_fields = spec.pop('data_fields')
         stype = spec.pop('type')
         if stype != cls._source_type:
            raise ValueError('invalid source type')

         return JSONSource(data_fields, io_loop=io_loop, http_client=http_client, **spec)
      except Exception, e:
         raise
      
   def parse(self, raw_data):
      data = None
      try:
         data = ujson.loads(raw_data)
      except ValueError, e:
         data = ujson.loads(raw_data[self._json_start_regex.search(raw_data).start():])
      except ValueError, e:
         raise
      
      if type(data) == list:
         return [self._serialize(x) for x in data]
      else:
         return self._serialize(data)

   def _serialize(self, obj):
      return {v: obj[k] for k,v in self._data_fields.iteritems()}

   def get_data_fields(self):
      return self._data_fields

   def query(self, obj, **kwargs):
      return ' '.join(["{}={}".format(o['symbol'], o['price_fix']) for o in obj])

class WebpageSource(CommonSource):
   _source_type='webpage'

   def __init__(self):
      pass
   
   @classmethod
   def load_from_spec(cls, spec):
      pass

   def parse(self, raw_data):
      pass

   def query(self, *args, **kwargs):
      pass

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
