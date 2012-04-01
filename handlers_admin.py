import backend.parsers as parsers
from backend.scheduled import ScheduledParse
from backend.models.rfp_entry import *
from handlers_base import *
from search import *
from backend.email import EmailSender

class AdminPanel(BaseHandler, HTMLRenderer):
    """Controller for the parser section of the admin panel"""

    @user_required
    @admin_required
    def get(self, status=None):
        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {}

        if status is not None:
            template_data['status'] = status

        self.show_rendered_html('templates/admin.html', template_data)

    @user_required
    def post(self):
        """Used to set parser settings and trigger parsers"""
        action = self.request.get('action')

        # Parse RFPs
        if action == 'parse':
            parser_name = self.request.get('parser')
            ignore_duplicates = self.request.get('ignore_duplicates')
            start_id = self.request.get('start_id')
            stop_on_dupe = self.request.get('stop_on_dupe')
            limit = self.request.get('parse_limit')

            if parser_name == 'merx':
                parser = parsers.MerxParser()
            elif parser_name == 'rfp.ca':
                parser = parsers.RFPParser()
            elif parser_name == 'satender':
                parser = parsers.STParser()
            (parsed, new) = ScheduledParse.parse(
                parser,
                ignore_duplicates is not '',
                (start_id is not "") and start_id or None,
                stop_on_dupe is not '',
                (limit is not "") and int(limit.strip()) or None)

            self.get('%d RFPs parsed, %d new stored. See logs.' % (parsed, new))

        # Delete all RFPs
        elif action == 'rfp_delete':
            while len(RFP.all().fetch(1)) is not 0:
                db.delete(RFP.all())

            while len(LiteralIndex.all().fetch(1)) is not 0:
                db.delete(LiteralIndex.all())

            self.get('All RFPs deleted successfully.')


class BaseEmailHandler:

    def send_rfps(self):
        logging.info('Starting RFP email updates...')
        emailSender = EmailSender()
        results = emailSender.send_rfps_to_subscribers()
        logging.info('Done RFP email updates')
        return results


class AdminSendEmailHandler(BaseHandler, BaseEmailHandler):

#    def send_rfps(self):
#        logging.info('Starting RFP email updates...')
#        emailSender = EmailSender()
#        results = emailSender.send_rfps_to_subscribers()
#        logging.info('Done RFP email updates')
#        return results
#

    @user_required
    @admin_required
    def post(self):
        """
            Used by admin panel.
            Show results of sending email updates to admin panel.
        """

        results = self.send_rfps()
        return AdminPanel(self.request, self.response).get('<br>'.join(results));