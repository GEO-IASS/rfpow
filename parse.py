import datetime
import logging
import webapp2
from backend.scheduled import ScheduledParse

class MainPage(webapp2.RequestHandler):
    """Web handler for the scheduled parser task"""
    def get(self):
        ignore_duplicates = self.request.get('ignore_duplicates')
        start_id = self.request.get('start_id')

        rfps = ScheduledParse.parse_merx( 
                ignore_duplicates is not "", 
                (start_id is not "") and start_id or None )
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('%d RFPs parsed. See admin console for more meaningful output.' % rfps)

#logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/parse', MainPage)],
                              debug=True)
