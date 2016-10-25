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

sources_map = {
   'google_finance_info': 'finance',
   'finviz_stock_info': 'finance',
   'openweather_by_city': 'weather',
   'fb_db_standings': 'sports',
   'theguardian_standings': 'sports',
   'sportinglife_results': 'sports',
   'sportinglife_fixtures': 'sports'
}

fb_db_leagues = {
   'epl': 'england-premier-league',
   'laliga': 'spain-liga-bbva',
   'bundesliga': 'germany-bundesliga',
   'sweden': 'sweden-allsvenskan',
   'ligue 1': 'france-ligue-1',
   'serie a': 'italy-serie-a'
}

theguardian_leagues = {
   'epl': 'premierleague',
   'ucl': 'championsleague',
   'laliga': 'laligafootball',
   'bundesliga': 'bundesligafootball',
   'ligue 1': 'ligue1football',
   'serie a': 'serieafootball',
   'europa': 'uefa-europa-league',   
}

sportinglife_leagues = {
   'epl': 'premier-league',
   'ucl': 'champions-league',
   'serie a': 'serie-a',
   'bundesliga': 'bundesliga',
   'ligue 1': 'ligue-1',
   'laliga': 'la-liga',
   'eredivisie': 'eredivisie',
   'fa-cup': 'fa-cup',
   'europa': 'europa-league'
}

class TextAnalyzer(object):
   _finance_keywords = ('symbol', 'stock', 'price', 'finance')
   _weather_keywords = ('weather', 'temp', 'temperature')
   _greetings = ('hey', 'hi', 'hello', 'sup', 'ciao', 'ola')
   _sports_keywords = {'pl', 'cl', 'scores', 'standings', 'board', 'league', 'goals', 'highlights'}

   def __init__(self):      
      self.companies = pd.read_csv(SHORT_COMPANIES_FP).Symbol.unique().tolist()
      
      world_cities = pd.read_csv(WORLD_CITIES_FP)
      self.cities = world_cities.name.str.lower().unique().tolist()
      self.countries = world_cities.country.str.lower().unique().tolist()

   def analyze(self, msg):
      # get the correct scraper/source
      source_name = None
      fetch_kwargs = {}
      query_kwargs = {}

      # check if msg is a city or country
      if msg in self.cities or msg in self.countries:
         source_name = 'openweather_by_city'
         fetch_kwargs = {'city': msg}
      elif 'finviz' in msg or 'fv' in msg:
         source_name = 'finviz_stock_info'
         fetch_kwargs = {'symbol': msg.split()[1]}
      elif 'fbdb' in msg:
         k = msg.split()[-1]
         source_name = 'fb_db_standings'
         league = fb_db_leagues[k]
         season = '2016' if k == 'sweden' else '2016-17'
         fetch_kwargs = {'league': league, 'season': season}
      elif 'standing' in msg:
         k = msg.split()[0]
         source_name = 'theguardian_standings'
         league = theguardian_leagues[k]
         fetch_kwargs = {'league': league}
      elif 'result' in msg:
         k = msg.split()[0]
         source_name = 'sportinglife_results'
         league = sportinglife_leagues[k]
         fetch_kwargs = {'league': league}
      elif 'fixture' in msg:
         k = msg.split()[0]
         source_name = 'sportinglife_fixtures'
         league = sportinglife_leagues[k]
         fetch_kwargs = {'league': league}         
      else:
         items = re.findall(r"[\w']+", msg)
         for item in items:
            if item in self._greetings:
               raise DefaultMessage

            if item.upper() in self.companies:
               source_name = 'google_finance_info'
               fetch_kwargs = {'symbols': ','.join(items)}
               break

            if item in self._weather_keywords:
               source_name = 'openweather_by_city'
               fetch_kwargs = {'city': 'philly'}
               break
      
      try:
         scraper_name = sources_map[source_name]
         return (scraper_name, source_name, fetch_kwargs, query_kwargs)
      except:
         raise UnableToAnalyzeText


            
      
      

