import config, services, logging, signal
from tornado import web, ioloop, gen, httpserver, netutil, process

logger = logging.getLogger(__name__)

class Application(web.Application):
   def __init__(self, config, db=None):
      super(Application, self).__init__([], **config)
      self.db = db

def app_handlers():
   handlers = services.pages.handlers()

   return handlers

def handle_signal(sig, frame):
   logger.debug('SIGNAL CAUGHT {}. Stopping event loop'.format(sig))
   ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)   
   

def run(run_config=None):
   signal.signal(signal.SIGINT, handle_signal)
   signal.signal(signal.SIGTERM, handle_signal)

   if run_config is None:
      run_config = {}
      
   if 'app_config' not in run_config:
      run_config['app_config'] = config.app_config
   
   if 'server_config' not in run_config:
      run_config['server_config'] = config.server_config

   
   app = Application(run_config['app_config'])

   
   port = run_config['server_config']['port']
   num_processes = run_config['server_config']['num_processes']
   
   sockets = netutil.bind_sockets(port)
   process.fork_processes(num_processes)

   server = httpserver.HTTPServer(app)
   server.add_sockets(sockets)
   
   app.add_handlers('.*', app_handlers())
   ioloop.IOLoop.current().start()
