import datetime
import logging
import webapp2
from backend.scheduled import ScheduledParse

class MainPage(webapp2.RequestHandler):
    """Web handler for the scheduled parser task"""
    def get(self):
        ignore_duplicates = self.request.get('ignore_duplicates')
        start_id = self.request.get('start_id')
        stop_on_dupe = self.request.get('stop_on_dupe')

        (parsed, new) = ScheduledParse.parse_merx( 
                ignore_duplicates is not '',
                (start_id is not "") and start_id or None,
                stop_on_dupe is not '')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('%d parsed, %d new. See admin logs.' % (parsed,new) )

#logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/parse', MainPage)],
                              debug=True)
