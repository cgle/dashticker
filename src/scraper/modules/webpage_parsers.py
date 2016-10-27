from tornado import ioloop, gen
from itertools import izip
import lxml.html
import ujson
import re

def load(name):
   return WEBPAGE_PARSERS[name]

#TODO: GENERALIZE PARSING TABLE/LIST

class DefaultParser(object):
   def __init__(self):
      pass
   
   def parse(self, raw_data):
      raise NotImplementedError
   
   def query(self, obj, **kwargs):
      return obj

class FinvizParser(DefaultParser):
   _base_url = 'http://finviz.com/'
   _snapshot_td_xpath = lxml.etree.XPath('//table[@class="snapshot-table2"]/tr/td')
   _chart_xpath = lxml.etree.XPath('//img[@id="chart0"]')

   def __init__(self):
      pass

   def parse(self, raw_data):
      tree = lxml.html.fromstring(raw_data)

      # get k,v pairs from the snapshot-table2
      snapshot_tds = self._snapshot_td_xpath(tree)
      snapshot_tds = [td.text_content().strip() for td in snapshot_tds]
      kv_pairs = {k:v for k,v in izip(*[iter(snapshot_tds)]*2)}
      
      # get chart src
      chart = self._base_url + self._chart_xpath(tree)[0].get('src')

      return {
         'data': kv_pairs,
         'chart': chart
      }
   
class SecDocListParser(DefaultParser):
   def __init__(self):
      pass

class SecReportParser(DefaultParser):
   def __init__(self):
      pass

class FBDBParser(DefaultParser):
   _main_tables_xpath = lxml.etree.XPath('//table[@class="table table-hover table-condensed"]')
   _base_url = 'http://footballdatabase.com/'
   def __init__(self):
      pass

   def parse(self, raw_data):
      tree = lxml.html.fromstring(raw_data)
      tables = self._main_tables_xpath(tree)
      total = self.strip_table(tables[0])
      home  = self.strip_table(tables[1])
      away  = self.strip_table(tables[2])

      logos = tables[0].cssselect('a')
      logos = {logo.text: self._base_url + logo.get('style')[22:-2] for logo in logos}

      return {
        'home': home,
        'away': away,
        'total': total,
        'logos': logos
      }
 
   @staticmethod
   def strip_table(el):
      ths = [th.text_content().strip() for th in el.cssselect('th')]
      trs = [[td.text_content().strip() for td in tr.cssselect('td')] for tr in el.cssselect('tbody tr')]
      return [ths] + trs

class TheGuardianStandingParser(DefaultParser):
   _tables_xpath = lxml.etree.XPath('//table[@class="table table--football table--league-table table--responsive-font table--striped"]')
   def __init__(self):
      pass

   def parse(self, raw_data):
      tree = lxml.html.fromstring(raw_data)
      tables = self._tables_xpath(tree)

      tables = [self.strip_table(table) for table in tables]

      return {
         'tables': tables
      }

   @staticmethod
   def strip_table(el):
      ## GP W D L F A GD Pts Form
      ths = [th.text_content().strip() for th in el.cssselect('th')]
      trs = [[td.text_content().strip() if i < len(ths)-1 else td.cssselect('span.team-result')
            for i,td in enumerate(tr.cssselect('td'))] for tr in el.cssselect('tbody tr')]

      ## Handle Form column      
      def handle_form(tr):
         spans = tr[-1]         
         # matches = [(span.get('data-score'),span.get('data-foe'),span.get('data-score-foe')) for span in spans]
         results = []         
         for span in spans:
            diff = int(span.get('data-score')) - int(span.get('data-score-foe'))
            results.append('W' if diff > 0 else 'D' if diff == 0 else 'L')
            
         tr[-1] = ','.join(results)
         return tr

      map(lambda tr: handle_form(tr), trs)

      return [ths] + trs


class SportingLifeResultsParser(DefaultParser):
   _sl_sections_xpath = lxml.etree.XPath('//section[@class="fr-gp"]')

   def __init__(self):
      pass

   def parse(self, raw_data):
      tree = lxml.html.fromstring(raw_data)
      sections = self._sl_sections_xpath(tree)
      
      return {'game_days': [self.strip_section(section) for section in sections]}

   @staticmethod
   def strip_section(el):
      date = el.cssselect('h3.hdr.t2')[0].text_content()
      def strip_game(t):
         team = t.cssselect('h4')[0].text_content()
         scorers = filter(lambda y: y, [x.strip() for x in t.cssselect('p')[0].text_content().split('\n')])
         return (team,scorers,len(scorers))

      games = [{'teams': [strip_game(t) for t in game.cssselect('.ixxt .ixx')]
              } for game in el.cssselect('li.fr-res')]
      return {'date': date, 'games': games}

class SportingLifeFixturesParser(DefaultParser):
   _sl_sections_xpath = lxml.etree.XPath('//section[@class="fr-gp"]')

   def __init__(self):
      pass

   def parse(self, raw_data):
      tree = lxml.html.fromstring(raw_data)
      sections = self._sl_sections_xpath(tree)
      
      return {'game_days': [self.strip_section(section) for section in sections]}

   @staticmethod
   def strip_section(el):
      date = el.cssselect('h3.hdr.t2')[0].text_content()
      def strip_game(t):
         team = t.cssselect(':not(.ixb.mobile-hdn)')[0].text_content()
         return team

      games = [{'teams': [strip_game(t) for t in game.cssselect('div.ix.ixf')],
                'time': game.cssselect('div.ix.ixt')[0].text_content()
              } for game in el.cssselect('li.fr-fix')]

      return {'date': date, 'games': games}

# init parser instances
WEBPAGE_PARSERS = {
   'default': DefaultParser(),
   'finviz': FinvizParser(),
   'sec_doct_list': SecDocListParser(),
   'sec_report': SecReportParser(),
   'fb_db': FBDBParser(),
   'theguardian_standings': TheGuardianStandingParser(),
   'sportinglife_results': SportingLifeResultsParser(),
   'sportinglife_fixtures': SportingLifeFixturesParser()
}   

