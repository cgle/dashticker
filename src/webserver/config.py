import os

DIRNAME = os.path.dirname(__file__)
STATIC_PATH = os.path.join(DIRNAME, 'static')
TEMPLATE_PATH = os.path.join(DIRNAME, 'templates')

cookie_secret = '$d4sH__#TICk3R!!@#'

app_config = {
   'template_path': TEMPLATE_PATH,
   'static_path': STATIC_PATH,
   'compress_response': True,
   'cookie_secret': cookie_secret,
   'debug': True
}

server_config = {
   'port' : 8000,
   'num_processes': 1
}
