import webapp2
import logging
from backend.scheduled import ScheduledParse
import backend.parsers as parsers
from backend.email import EmailSender
class CronMerx(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""
    def get(self):
        logging.info( 'Starting scheduled parse for Merx' )
        parser = parsers.MerxParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronRFPEmailUpdates(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""
    def get(self):
        logging.info( 'Starting RFP email updates...' )
        emailSender = EmailSender()
        emailSender.send("john.sintal@gmail.com", "Subject", "john.sintal@gmail.com", "<b>hi</b>")
        logging.info( 'Done RFP email updates...' )

