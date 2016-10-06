from tornado import websocket, ioloop, gen, web
import bot, logging
import uuid

logger = logging.getLogger(__name__)

class BotWSHandler(websocket.WebSocketHandler):
   def __init__(self, *args, **kwargs):
      self._uid = uuid.uuid4().bytes

      self.bot = kwargs.pop('bot')
      self.bot.add_handler(self)
      super(BotWSHandler, self).__init__(*args, **kwargs)      

   def uid(self):
      return self._uid

   def open(self):
      logger.debug('ws connection opened')
   
   @gen.coroutine
   def on_message(self, message):
      yield self.bot.handle_message(message, self)

   def on_close(self):
      logger.debug('ws connection closed')
      self.bot.remove_handler(self._uid)

def handlers(bot=None):
   return [
      (r'/ws/bot', BotWSHandler, dict(bot=bot)),
   ]
