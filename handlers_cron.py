import webapp2
import logging
from backend.scheduled import ScheduledParse
import backend.parsers as parsers
from backend.email import EmailSender
from handlers_base import HTMLRenderer
from handlers_admin import *

class CronMerx(webapp2.RequestHandler):
    """Handler for scheduled parser for Merx"""

    def get(self):
        logging.info( 'Starting scheduled parse for Merx' )
        parser = parsers.MerxParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronRfpdotca(webapp2.RequestHandler):
    """Handler for scheduled parser for RFP.ca"""

    def get(self):
        logging.info( 'Starting scheduled parse for rfp.ca' )
        parser = parsers.RFPParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronSaTenders(webapp2.RequestHandler):
    """Handler for scheduled parser for RFP.ca"""

    def get(self):
        logging.info( 'Starting scheduled parse for SaTenders' )
        parser = parsers.STParser()
        (parsed, new) = ScheduledParse.parse(parser, stop_on_dupe=True)

class CronSendEmail(webapp2.RequestHandler, HTMLRenderer):
    """Handler for scheduled parser for sending emails"""

    def send_rfps(self):
        logging.info('Starting RFP email updates...')
        emailSender = EmailSender()
        results = emailSender.send_rfps_to_subscribers()
        logging.info('Done RFP email updates')
        return results

    def get(self):
        """Used by cron."""

        self.send_rfps()

    def post(self):
        """
            Used by admin panel.

            Show results of sending email updates to admin panel.
        """

        results = self.send_rfps()

        # reuse admin panel handler
        return AdminPanel( self.request, self.response ).get( '<br>'.join(results) );
