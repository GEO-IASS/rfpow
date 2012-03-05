import webapp2
import jinja2
import os
import logging
from backend.scheduled import ScheduledParse

class CronMerx(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""
    def get(self):
        logging.info( 'Starting scheduled parse for Merx' )
        (parsed, new) = ScheduledParse.parse_merx(stop_on_dupe=True)
