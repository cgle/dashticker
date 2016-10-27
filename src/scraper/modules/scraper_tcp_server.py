from tornado import gen, web, tcpserver, iostream
import struct, socket
import logging, ujson
from bridge import message_factory
logger = logging.getLogger(__name__)

# connection from BOT to SCRAPER
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
   def on_connect(self):
      yield self.dispatch_client()

   @gen.coroutine
   def dispatch_client(self):
      try:
         while True:
            data = yield self.stream.read_bytes(4)
            logger.debug('RECEIVING DATA: {} bytes'.format(len(data)))
            msg_len = struct.unpack('I', data)[0]
            data = yield self.stream.read_bytes(msg_len)
            logger.debug('RECEIVING DATA: {} bytes'.format(len(data)))

            yield self.server.handle_request(self, data)

      except iostream.StreamClosedError,e:
         logger.error(e)         

class ScraperTCPServer(tcpserver.TCPServer):
   def __init__(self,*args, **kwargs):
      super(ScraperTCPServer, self).__init__(*args, **kwargs)
      self.scrapers = {}      
      self.msg_factory = message_factory.MessageFactory()

   def add_scraper(self, scraper):
      self.scrapers[scraper.name] = scraper

   def remove_scraper(self, name):
      try:
         del self.scrapers[name]
      except KeyError, e:
         logger.error(e)
   
   def get_scraper(self, name):
      try:
         return self.scrapers[name]
      except KeyError, e:
         raise

   # on connection with bot, hand off to connection.on_connect()
   @gen.coroutine
   def handle_stream(self, stream, address):
      connection = ScraperTCPConnection(stream, self)
      yield connection.on_connect()

   @gen.coroutine
   def handle_request(self, conn, data):
      input_msg = self.msg_factory.decode_input(data)

      bot_hid = input_msg.bot_hid
      scraper_name = input_msg.scraper_name
      source_name = input_msg.source_name
      fetch_kwargs = ujson.loads(input_msg.fetch_kwargs)
      query_kwargs = ujson.loads(input_msg.query_kwargs)

      output_msg = 'bot cannot understand request'
      
      try:
         scraper = self.scrapers[scraper_name]
         source = scraper.get_source(source_name)
         response = yield source.fetch(**fetch_kwargs)
         obj = source.parse(response.body)
         out = source.query(obj, **query_kwargs)
         
         # add metadata
         out = {
            'content': out,
            'scraper': scraper_name,
            'source': source_name
         }

         # dumps to string output_msg
         output_msg = ujson.dumps(out)
      
      except AttributeError, e:
         output_msg = 'unable to fetch data, please try again. Error {}'.format(e)

      except Exception, e:
         output_msg = str(e)
          
      output_msg = self.msg_factory.encode_output(bot_hid, output_msg)
      yield conn.stream.write(output_msg)

