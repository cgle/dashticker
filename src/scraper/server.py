import logging, signal, os, ujson
import config
import datetime
from tornado import netutil, ioloop, process, httpclient, gen
import uvloop
from services import common_sources
from services import scraper_tcp_server

logger = logging.getLogger(__name__)
ioloop.IOLoop.configure(uvloop.UVLoop)
httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

def handle_signal(sig, frame):
   logger.debug('SIGNAL CAUGHT {}. Stopping event loop'.format(sig))
   ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)

@gen.coroutine
def setup_scrapers(port):
   io_loop = ioloop.IOLoop.instance()
   http_client = httpclient.AsyncHTTPClient(io_loop=io_loop)
   scraper_server = scraper_tcp_server.ScraperTCPServer()
   scraper_server.listen(port)
   

   # load sources from json
   finance_fp = os.path.join(config.DIRNAME, 'services', 'finance.json')
   finance_sources = ujson.loads(open(finance_fp, 'r').read())['sources']   

   google_source = common_sources.JSONSource.load_from_spec(finance_sources[0], io_loop=io_loop, http_client=http_client)

   main_scraper = common_sources.CommonScraper('finance', tcp_server=scraper_server)
   main_scraper.add_source(google_source)
   
def run(run_config=None):
   signal.signal(signal.SIGINT, handle_signal)
   signal.signal(signal.SIGTERM, handle_signal)

   run_config = {} if run_config is None else run_config

   if 'server_config' not in run_config:
      run_config['server_config'] = config.server_config
   
   # fork processes
   port = run_config['server_config']['port']
   num_processes = run_config['server_config']['num_processes']

   process.fork_processes(num_processes, max_restarts=1)
   io_loop = ioloop.IOLoop.current()
   
   # setup scrapers
   setup_scrapers(port)

   io_loop.start()


