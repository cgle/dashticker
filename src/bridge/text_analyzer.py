import pandas as pd
import ujson
import re, os

DIRNAME = os.path.dirname(__file__)
SHORT_COMPANIES_FP = os.path.join(DIRNAME, 'short_companies.csv')
US_CITIES_FP = os.path.join(DIRNAME, 'us_cities.csv')
WORLD_CITIES_FP = os.path.join(DIRNAME, 'world-cities.csv')

class UnableToAnalyzeText(Exception):
   def __init__(self):
      Exception.__init__(self, 'cannot comprehend the message :(')

class DefaultMessage(Exception):
   def __init__(self):
      Exception.__init__(self, 'hey, welcome to dashticker :)')

scrapers_map = {
   'finance': {
      'scraper_name': 'finance',
      'source_name': 'google_finance_info'      
   },
   'weather': {
      'scraper_name': 'weather',
      'source_name': 'openweather_by_city'
   }
}

class TextAnalyzer(object):
   _finance_keywords = ('symbol', 'stock', 'price', 'finance')
   _weather_keywords = ('weather', 'temp', 'temperature')
   _greetings = ('hey', 'hi', 'hello', 'sup', 'ciao', 'ola')

   def __init__(self):
      
      self.companies = pd.read_csv(SHORT_COMPANIES_FP).Symbol.unique().tolist()
      
      world_cities = pd.read_csv(WORLD_CITIES_FP)

      self.cities = world_cities.name.str.lower().unique().tolist()
      self.countries = world_cities.country.str.lower().unique().tolist()

   def analyze(self, msg):
      items = re.findall(r"[\w']+", msg)
      
      # get the correct scraper/source
      scraper = None
      fetch_kwargs = {}
      query_kwargs = {}

      for item in items:
         if item in self._greetings:
            raise DefaultMessage

         if item.upper() in self.companies:
            scraper = 'finance'
            if not fetch_kwargs:
               fetch_kwargs['symbols'] = ''
            fetch_kwargs['symbols'] += item + ','

         if item in self._weather_keywords:
            scraper = 'weather'
            fetch_kwargs = {'city': 'philly'}
            break

      if not scraper and (msg in self.cities or msg in self.countries):
         scraper = 'weather'
         fetch_kwargs = {'city': msg}
      
      try:
         scraper = scrapers_map[scraper]
         scraper_name = scraper['scraper_name']
         source_name = scraper['source_name']         
         return (scraper_name, source_name, fetch_kwargs, query_kwargs)
      except:
         raise UnableToAnalyzeText


            
      
      

