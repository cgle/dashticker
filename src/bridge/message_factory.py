import struct
from tornado import gen, iostream
import msg_pb2
import ujson

class MessageFactory(object):
   def __init__(self):
      pass

   def decode_input(self, data):
      msg = msg_pb2.InputMsg()
      msg.ParseFromString(data)
      return msg

   def decode_output(self, data):
      msg = msg_pb2.OutputMsg()
      msg.ParseFromString(data)
      return msg
   
   # return output msg ready to send over tcp
   def encode_output(self, bot_hid, msg):
      data = msg_pb2.OutputMsg()
      data.bot_hid = bot_hid
      data.msg = msg
      
      output_msg = self._generate_msg(data.SerializeToString())
      return output_msg

   # return input msg ready to send over tcp
   def encode_input(self, bot_hid, scraper_name, source_name, fetch_kwargs, query_kwargs):
      data = msg_pb2.InputMsg()
      data.bot_hid = bot_hid
      data.scraper_name = scraper_name
      data.source_name = source_name
      data.fetch_kwargs = ujson.dumps(fetch_kwargs)
      data.query_kwargs = ujson.dumps(query_kwargs)
      
      input_msg = self._generate_msg(data.SerializeToString())
      return input_msg

   def _generate_msg(self, data):
      data_len = len(data)
      msg = struct.pack('I{}s'.format(data_len), data_len, data)
      return msg

