import webapp2
import logging
from backend.scheduled import ScheduledParse
import backend.parsers as parsers
from backend.email import EmailSender
from handlers_base import HTMLRenderer

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

class CronSendEmail(webapp2.RequestHandler, HTMLRenderer):
    """Handler for scheduled parser for sending emails"""

    def send_rfps(self):
        logging.info('Starting RFP email updates...')
        emailSender = EmailSender()
        results = emailSender.send_rfps_to_subscribers()
        logging.info('Done RFP email updates')
        return results

    def get(self):
        """
            Used by cron.
        """

        self.send_rfps()


    def post(self):
        """
            Used by admin panel. Shows results of what sending of email updates after sending the emails.
        """
        results = self.send_rfps()
        template_data = {}
        if results is not None:
            template_data['results'] = results
        self.show_rendered_html('templates/send_email_log.html', template_data)
