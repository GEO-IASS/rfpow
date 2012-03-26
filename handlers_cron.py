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

class CronSendEmail(webapp2.RequestHandler):
    """Handler for scheduled parser for sending emails"""

    def get(self):
        logging.info( 'Starting RFP email updates...' )
        emailSender = EmailSender()

        # if run by cron, don't pass in response, which down line shows no json response
        if not 'cron' in self.request.url:
            response = self.response
        else:
            response = None

        emailSender.send_rfps_to_subscribers(response)
        logging.info( 'Done RFP email updates...' )

