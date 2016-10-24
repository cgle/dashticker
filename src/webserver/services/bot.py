from tornado import web, gen, ioloop, iostream, tcpclient, queues
import logging, socket
import time, datetime
import struct, ujson
from bridge import message_factory, text_analyzer

logger = logging.getLogger(__name__)

class CommonBot(object):
   def __init__(self, host=None, port=None):
      self.io_loop = ioloop.IOLoop.instance()
      self.host = host
      self.port = port
      self.stream = None
      self.handlers = {} 
      self.msg_factory = message_factory.MessageFactory()
      self.txt_analyzer = text_analyzer.TextAnalyzer()
      
      self._delay_timeouts = {}
      self._delay_secs = datetime.timedelta(seconds=3)

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
      message = message.lower()
      
      # keep track of bot_ws handle id to return msg later on
      bot_hid = handler.hid()     
      
      if bot_hid not in self._delay_timeouts:
         logger.debug('adding delay timeout to ioloop')      
         self._delay_timeouts[bot_hid] = self.io_loop.add_timeout(self._delay_secs, 
                                                              self.send_message_to_client,
                                                              bot_hid, 'processing...')
      
      try:
         input_args = self.txt_analyzer.analyze(message)
         input_msg = self.msg_factory.encode_input(bot_hid, *input_args)
         yield self.send_message_to_bridge(input_msg)

      except Exception, e:
         yield self.send_message_to_client(bot_hid, str(e))

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

   def _reset_bridge(self):
      self._close_bridge()
      self._open_bridge()      

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
            yield self.send_message_to_client(bot_hid, msg)
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
   def send_message_to_client(self, handler_id, message):
      try:
         self.io_loop.remove_timeout(self._delay_timeouts[handler_id])
         logger.debug('removing delay timeout')         
         del self._delay_timeouts[handler_id]
      except KeyError:
         pass

      try:
         yield self.handlers[handler_id].write_message(message)
      except Exception, e:
         logger.error(e)

         
      

      
   
      
