import os, json, logging
from webserver import server

def main():
   #TODO logging
   logging.basicConfig(level=logging.DEBUG)
   server.run()

if __name__ == '__main__':
   main()
   
