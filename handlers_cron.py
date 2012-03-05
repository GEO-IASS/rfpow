import webapp2
import jinja2
import os
import logging
from backend.scheduled import ScheduledParse

class Merx(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""
    def get(self):
        logging.info( 'Starting scheduled parse for Merx' )
        (parsed, new) = ScheduledParse.parse_merx(stop_on_dupe=True)

app = webapp2.WSGIApplication(
        [('/cron/merx', Merx)],
        debug=True,
        config= {
            'webapp2_extras.sessions':
            { 'secret_key': '6023a964-ea67-4965-b8c1-8b098b87a51a' }
        })
