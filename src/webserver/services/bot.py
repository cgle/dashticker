from tornado import web, gen, ioloop, iostream, tcpclient
import logging, socket
import time, datetime
import struct, ujson
from bridge import message_factory

logger = logging.getLogger(__name__)



class CommonBot(object):
   def __init__(self, host=None, port=None):
      self.io_loop = ioloop.IOLoop.instance()
      self.host = host
      self.port = port
      self.stream = None
      self.handlers = {} 
      self.msg_factory = message_factory.MessageFactory()
      
      #TODO delayed msg queues 

   def add_handler(self, handler):
      self.handlers[handler.hid()] = handler

   def remove_handler(self, hid):
      try:
         del self.handlers[hid]
      except KeyError, e:
         logger.error(e)

   @gen.coroutine
   def handle_ws_message(self, message, handler):      
      logger.debug('bot received message: {}'.format(message))
      message = message.encode('utf-8')
      bot_hid = handler.hid()
      
      #TODO: auto generate this
      scraper_name = 'finance'
      source_name = 'google_finance_info'
      fetch_kwargs = {'symbols': message}
      query_kwargs = {'symbol': None}

      input_msg = self.msg_factory.encode_input(bot_hid, scraper_name, source_name, 
                                                fetch_kwargs, query_kwargs)

      yield self.send_message_to_bridge(input_msg)

   @gen.coroutine
   def start(self):
      yield self._open_bridge()
   
   @gen.coroutine
   def _open_bridge(self):
      if not self.stream:
         self.stream = yield tcpclient.TCPClient(io_loop=self.io_loop)\
                                      .connect(self.host, self.port)
         
         yield self._handle_read_bridge()

   def _close_bridge(self):
      if self.stream:
         self.stream.close()
         self.stream = None

   @gen.coroutine
   def _handle_read_bridge(self):
      try:
         while True:
            data = yield self.stream.read_bytes(4)
            msg_len = struct.unpack('I', data)[0]
            data = yield self.stream.read_bytes(msg_len)
            logger.debug('READING FROM BRIDGE {} bytes'.format(len(data)))
            output_msg = self.msg_factory.decode_output(data)
            bot_hid = output_msg.bot_hid
            msg = output_msg.msg      
            yield self.send_message_to_client(msg, bot_hid)
      except iostream.StreamClosedError, e:
         logger.error(e)
         self._close_bridge()

   @gen.coroutine
   def send_message_to_bridge(self, message):
      logger.debug('SENDING TO BRIDGE {} bytes'.format(len(message)))
      try:
         yield self.stream.write(message)
      except Exception, e:
         logger.error(e)
   
   @gen.coroutine
   def send_message_to_client(self, message, handler_hid):
      try:
         yield self.handlers[handler_hid].write_message(message)
      except Exception, e:
         logger.error(e)

         
      

      
   
      
