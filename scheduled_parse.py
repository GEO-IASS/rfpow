import datetime
import logging
import webapp2
from backend.scheduled import ScheduledParse

class MainPage(webapp2.RequestHandler):
    """Web handler for the scheduled parser task"""
    def get(self):
        ScheduledParse.parse_merx() 
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('test')

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/parse', MainPage)],
                              debug=True)
