import logging
from scraper import server

def main():
   logging.basicConfig(level=logging.DEBUG)
   server.run()

if __name__ == '__main__':
   main()
