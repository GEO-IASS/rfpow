import logging
from google.appengine.api import mail
from backend.models.rfp_entry import RFP
from backend.models.subscription import Subscription
from handlers_base import HTMLRenderer
from webapp2_extras.appengine.auth.models import User
from ndb import query

import datetime

default_sender = "rfpow301demo@gmail.com"


class EmailSender(HTMLRenderer):
    """
        EmailSender is responsible for gathering RFP data for each user who has subscribed to
        email updates, then sending that data via email.
    """


    def send_rfps_to_subscribers(self):
        """
            As the function name implies, all subscribed users will receive an RFP update to their
            email accounts. By comparing an RFP's parse date to a subscription's last update date,
            we ensure dups aren't being sent out.

            Returns a list of results based on what happened for each subscription.

        """

        results = []
        subs = Subscription.all()
        for sub in subs:

            try:

                # Grab what user info, add first, last name later
                user = User.query(query.FilterNode('username', '=', sub.username)).get()

                # Ensure the the sub's username is associated with an actual account
                # by checking if the email exists.
                if user.email:
                    self._send_rfps_to_subscribers(sub, user.first_name, user.email, results)
                else:
                    msg = 'No email found for username: %s  and keyword: %s' % (sub.username, sub.keyword)

                    logging.info(msg)
                    results.append('Error: ' + msg)
            except:
                msg = 'Problem with sending RFPs for some subscription, maybe bad user object'
                logging.info(msg)
                results.append('Error: ' + msg)


        return results


    def _send_rfps_to_subscribers(self, sub, first_name, email, results):
        """
            Helper function to assist in testing.
        """

        try:
            # Query RFPs based on this subscription's keyword
            rfp_list = RFP.search(phrase=sub.keyword, date=sub.last_updated, limit=10)

            if rfp_list and len(rfp_list) > 0:
                template_values = {
                    "rfps": rfp_list,
                    "name": first_name,
                    'search_text': sub.keyword,
                    'is_admin': False,
                    'search_uri': 'http://rfpow301.appspot.com/rfp/search/',
                    'permalink_uri': 'http://rfpow301.appspot.com/rfp/'
                }

                subject = "New RFPs for \"%s\" : RFPow!" % sub.keyword
                self.send(subject, email, template_values)

                # Update the last update time so we know to not send dups on next cron
                sub.last_updated = datetime.datetime.now().date()
                sub.put()

                msg = "Found %d RFPs for %s with keyword '%s' for email: %s" %\
                      (len(rfp_list), sub.username, sub.keyword, email)

                logging.info(msg)
                results.append(msg)
            else:
                msg = 'No RFPs found for username: %s and keyword: %s' % (sub.username, sub.keyword)

                logging.info(msg)
                results.append(msg)
        except:
            msg = 'Problem with sending a sub, probably None object'
            logging.info(msg)
            results.append(msg)



    def send(self, subject="RFP Update", to="", template_values=[]):
        """
            Sends an email out based on the args given. Thin wrapper
            for Google's API.
        """
        try:
            html = self.get_rendered_html('templates/email.html', template_values)

            message = mail.EmailMessage()
            message.sender = default_sender
            message.subject = subject
            message.to = to
            message.html = html

            message.send()
            logging.info('Success sending email for ' + to)
        except:
            logging.info('Failed to send email for ' + to)


