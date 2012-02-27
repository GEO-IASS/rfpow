import datetime
import logging
import webapp2
from backend.scheduled import ScheduledParse

class MainPage(webapp2.RequestHandler):
    """Web handler for the scheduled parser task"""
    def get(self):
        rfps = ScheduledParse.parse_merx() 
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('%d RFPs parsed. See admin console.' % rfps)

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/parse', MainPage)],
                              debug=True)
