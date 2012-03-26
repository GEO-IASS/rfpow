import logging
from google.appengine.api import mail
from backend.models.rfp_entry import RFP
from backend.models.subscription import Subscription
from handlers_base import HTMLRenderer

from webapp2_extras.appengine.auth.models import User
from handlers_base import JSONWriter
from ndb import query
from backend.models import subscription
import datetime

# TODO: probably want a less personal email
default_sender = "john.sintal@gmail.com"


class EmailSender(HTMLRenderer, JSONWriter):
    """
        EmailSender is responsible for gathering RFP data for each user who has subscribed to
        email updates, then sending that data via email.
    """
    def get_first_last_name(self, username):
        """
            Returns the email for the user with username given, otherwise None.
        """

        user = User.query(query.FilterNode('username', '=', username)).get()
        if user:
            return user.first_name + user.last_name
        else:
            return None

    def get_email(self, username):
        """
            Returns the email for the user with username given, otherwise None.
        """

        user = User.query(query.FilterNode('username', '=', username)).get()
        if user:
            return user.email
        else:
            return None

    def send_rfps_to_subscribers(self, response=None):
        """
            As the function name implies, all subscribed users will receive an RFP update to their
            email accounts. By comparing an RFP's parse date to a subscription's last update date,
            we ensure dups aren't being sent out.

            If response is None, then json response is not given back to client.

        """
        subscription.create_subscription("john3", "Gaming")

        subs = Subscription.all()
        for sub in subs:

            # Grab what user info, add first, last name later
            email = self.get_email(sub.username)

            # Ensure the the sub's username is associated with an actual account
            # by checking if the email exists.
            if (email):
                first_last_name = self.get_first_last_name(sub.username)

                # Query RFPs based on this subscription's keyword
                # TODO: Add  where {rfp}.parse_date > sub.last_updated
                rfp_list = RFP.search(phrase=sub.keyword, limit=10)

                if (rfp_list and len(rfp_list) > 0):

                    template_values = {"rfps" : rfp_list,
                                       "name" : first_last_name,
                                       'search_text' : sub.keyword,
                                       'is_admin' : False}

                    subject = "RFPow! Updates: " + sub.keyword
                    self.send(subject, email, template_values)

                    # Update the last update time so we know to not send dups on next cron
                    sub.last_updated = datetime.datetime.now().date()
                    sub.put()

                    msg = "Found %d RFPs for %s with keyword %s for email: %s" % (len(rfp_list), sub.username,
                                                                                 sub.keyword, email)
                    logging.info(msg)
                    self.write_json_email(self.status_success, msg, response)

                else:
                    msg = 'No RFPs found for username: %s and keyword: %s' % (sub.username, sub.keyword)

                    logging.info(msg)
                    self.write_json_email(self.status_error, msg, response)
            else:
                msg = 'No email found for username: %s  and keyword: %s' % (sub.username, sub.keyword)
                logging.info(msg)
                self.write_json_email(self.status_error, msg, response)




    def send(self, subject="RFP Update", to="", template_values=[]):
        """
            Sends an email out based on the args given. Thin wrapper
            for Google's API.
        """

        html = self.get_rendered_html('templates/rfp_table.html', template_values)

        message = mail.EmailMessage()
        message.sender = default_sender
        message.subject = subject
        message.to = to
        message.html = html
        try:
            message.send()
            logging.info( 'Success sending email for ' + to )
        except:
            logging.info( 'Failed to send email for ' + to )


