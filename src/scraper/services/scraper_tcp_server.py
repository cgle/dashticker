from tornado import gen, web, tcpserver, iostream
import struct, socket
import logging

logger = logging.getLogger(__name__)


class ScraperTCPConnection(object):
   def __init__(self, stream, server):
      self.stream = stream
      self.server = server

      self.stream.socket.setsockopt(
         socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      self.stream.socket.setsockopt(
         socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)

      self.stream.set_close_callback(self.on_disconnect)
   
   @gen.coroutine
   def on_disconnect(self):
      logger.debug('scraper tcp client disconnected')
   
   @gen.coroutine
   def dispatch_client(self):
      try:
         while True:
            data = yield self.stream.read_bytes(4)
            logger.debug('RECEIVING DATA: {}'.format(data))
            msg_len = struct.unpack('I', data)[0]
            print msg_len
            data = yield self.stream.read_bytes(msg_len)
            
            logger.debug('RECEIVING DATA: {}'.format(data))
            handler_uid = data[:16]
            msg = data[16:]
            yield self.server.handle_request(msg, self.stream, handler_uid)
      except iostream.StreamClosedError,e:
         logger.error(e)
   
   @gen.coroutine
   def on_connect(self):
      yield self.dispatch_client()

class ScraperTCPServer(tcpserver.TCPServer):
   def __init__(self, *args, **kwargs):
      super(ScraperTCPServer, self).__init__(*args, **kwargs)
      self.scrapers = {}

   @gen.coroutine
   def handle_stream(self, stream, address):
      connection = ScraperTCPConnection(stream, self)
      yield connection.on_connect()

   def add_scraper(self, scraper):
      self.scrapers[scraper.name] = scraper

   def remove_scraper(self, name):
      try:
         del self.scrapers[name]
      except KeyError, e:
         logger.error(e)
   
   @gen.coroutine
   def handle_request(self, msg, stream, handler_uid):
      response = yield self.scrapers['finance'].fetch(symbols=msg)
      data = response.body
      msg_len = 16 + len(data)
      msg = struct.pack('16s{}s'.format(len(data)), handler_uid, data)
      yield stream.write(msg)
