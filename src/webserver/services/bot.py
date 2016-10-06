from tornado import web, gen, ioloop
import logging, socket
import time, datetime
import struct, ujson

logger = logging.getLogger(__name__)

class CommonBot(object):
   def __init__(self, host=None, port=None):
      self.io_loop = ioloop.IOLoop.instance()
      self.host = host
      self.port = port
      self.sock = None
      self.handlers = {}      
         
   @gen.coroutine
   def handle_message(self, message, handler):      
      logger.debug('bot received message: {}'.format(message))
      message = message.encode('utf-8')
      uid = handler.uid()
      msg_len = 16 + len(message)
      bridge_msg = struct.pack('I16s{}s'.format(len(message)), msg_len, uid, message)
      yield handler.write_message('processing...')
      self.send_message_to_bridge(bridge_msg)

   def add_handler(self, handler):
      self.handlers[handler.uid()] = handler

   def remove_handler(self, uid):
      try:
         del self.handlers[uid]
      except KeyError, e:
         logger.error(e)
            
   def start(self):
      self._open_bridge()
   
   def _open_bridge(self):
      if not self.sock:
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
         self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         self.sock.connect((self.host, self.port))
         self.sock.setblocking(0)
         self.io_loop.add_handler(
            self.sock.fileno(), self._handle_bridge_events, self.io_loop.ERROR)
         self.io_loop.update_handler(self.sock.fileno(), self.io_loop.READ)

   def _handle_bridge_events(self, fd, events):
      if not self.sock:
         return
      if events & self.io_loop.READ:
         self._handle_read()
      if events & self.io_loop.ERROR:
         self._close_bridge()


   def _close_bridge(self):
      try:
         self.io_loop.remove_handler(self.sock.fileno())
      except:
         pass

      if self.sock:
         self.sock.close()
         self.sock = None
   
   @gen.coroutine
   def _handle_read(self):
      logger.debug('ON READING BRIDGE')
      try:
         chunk = self.sock.recv(4096)
      except socket.error, e:
         if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
            return
         else:
            logger.error(e)
            self._close_bridge()
            return

      uid = chunk[:16]
      data = ujson.loads(chunk[16:][3:])[0]
      msg = 'stock price {}: {}'.format(data['t'], data['l'])
      yield self.send_message_to_client(msg, uid)

   def send_message_to_bridge(self, message):
      logger.debug('SENDING TO BRIDGE {} bytes'.format(len(message)))
      try:
         self.sock.send(message)
      except Exception, e:
         logger.error(e)
   
   @gen.coroutine
   def send_message_to_client(self, message, handler_uid):
      try:
         yield self.handlers[handler_uid].write_message(message)
      except Exception, e:
         logger.error(e)

         
      

      
   
      
