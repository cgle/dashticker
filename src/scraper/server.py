import logging, signal
import config
import datetime
from tornado import netutil, ioloop, process, httpclient, gen
import uvloop
import services.common

logger = logging.getLogger(__name__)
ioloop.IOLoop.configure(uvloop.UVLoop)
httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

def handle_signal(sig, frame):
   logger.debug('SIGNAL CAUGHT {}. Stopping event loop'.format(sig))
   ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)

def test():
   io_loop = ioloop.IOLoop.instance()
   http_client = httpclient.AsyncHTTPClient(io_loop=io_loop)
   a = services.common.CommonSource(name='test', url_pattern='http://localhost:8000', io_loop=io_loop, http_client=http_client)
   
   interval = datetime.timedelta(seconds=5)
   a.start_timer(url='http://localhost:8000', interval=interval)

def run(run_config=None):
   signal.signal(signal.SIGINT, handle_signal)
   signal.signal(signal.SIGTERM, handle_signal)

   run_config = {} if run_config is None else run_config

   if 'server_config' not in run_config:
      run_config['server_config'] = config.server_config
   
   # fork processes
   port = run_config['server_config']['port']
   num_processes = run_config['server_config']['num_processes']

   sockets = netutil.bind_sockets(port)
   process.fork_processes(num_processes, max_restarts=1)
   io_loop = ioloop.IOLoop.current()

   test()
   io_loop.start()


