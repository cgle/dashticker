from tornado import web

class IndexHandler(web.RequestHandler):
   @web.asynchronous
   def get(self):
      self.render('index.html')

class AboutHandler(web.RequestHandler):
   @web.asynchronous
   def get(self):
      self.render('about.html')

class ContactHandler(web.RequestHandler):
   @web.asynchronous
   def get(self):
      self.render('contact.html')

def handlers():
   return [
      (r'/', IndexHandler),
      (r'/about', AboutHandler),
      (r'/contact', ContactHandler),]
