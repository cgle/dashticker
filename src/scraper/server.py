import logging, signal, os, ujson
import config
import datetime
from tornado import netutil, ioloop, process, httpclient, gen
import uvloop
from services import common_sources, common_scrapers, scraper_tcp_server

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
  
   #finance scraper
   finance_fp = os.path.join(config.DIRNAME, 'services', 'finance.json')   
   finance_sources = ujson.loads(open(finance_fp, 'r').read())['sources']   
   google_source = common_sources.JSONSource.load_from_spec(finance_sources[0], io_loop=io_loop, http_client=http_client)
   finviz_source = common_sources.WebpageSource.load_from_spec(finance_sources[1], io_loop=io_loop, http_client=http_client)

   finance_scraper = common_scrapers.CommonScraper('finance', tcp_server=scraper_server)
   finance_scraper.add_source(google_source)
   finance_scraper.add_source(finviz_source)

   #weather scraper
   weather_fp = os.path.join(config.DIRNAME, 'services', 'weather.json')
   weather_sources = ujson.loads(open(weather_fp, 'r').read())['sources']
   openweather_source = common_sources.JSONSource.load_from_spec(weather_sources[0], io_loop=io_loop, http_client=http_client)
   
   weather_scraper = common_scrapers.CommonScraper('weather', tcp_server=scraper_server)
   weather_scraper.add_source(openweather_source)
   
   #sports scraper
   sports_fp = os.path.join(config.DIRNAME, 'services', 'sports.json')
   sports_sources = ujson.loads(open(sports_fp, 'r').read())['sources']
   
   fb_db_source = common_sources.WebpageSource.load_from_spec(sports_sources[0], io_loop=io_loop, http_client=http_client)
   theguardian_st_source = common_sources.WebpageSource.load_from_spec(sports_sources[1], io_loop=io_loop, http_client=http_client)
   sportinglife_rs_source = common_sources.WebpageSource.load_from_spec(sports_sources[3], io_loop=io_loop, http_client=http_client)
   sportinglife_fx_source = common_sources.WebpageSource.load_from_spec(sports_sources[4], io_loop=io_loop, http_client=http_client)

   sports_scraper = common_scrapers.CommonScraper('sports', tcp_server=scraper_server)
   sports_scraper.add_source(fb_db_source)
   sports_scraper.add_source(theguardian_st_source)
   sports_scraper.add_source(sportinglife_rs_source)
   sports_scraper.add_source(sportinglife_fx_source)

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


