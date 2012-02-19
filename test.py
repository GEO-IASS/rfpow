import webapp2
from Parsers import MerxParser

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( MerxParser.get_latest() )

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
