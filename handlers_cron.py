import webapp2
import logging
from backend.scheduled import ScheduledParse
import backend.parsers as parsers
import backend.rfpdotca_parser as parser2
from backend.email import EmailSender

class CronMerx(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""

    def get(self):
        logging.info( 'Starting scheduled parse for Merx' )
        parser = parsers.MerxParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronRfpdotca(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""

    def get(self):
        logging.info( 'Starting scheduled parse for rfp.ca' )
        parser = parser2.RFPParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronRFPEmailUpdates(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""

    def get(self):
        logging.info( 'Starting RFP email updates...' )
        emailSender = EmailSender()
        #emailSender.send(, "Subject", "john.sintal@gmail.com", [])
        emailSender.send_rfps_to_subscribers()

        logging.info( 'Done RFP email updates...' )

