import logging
from google.appengine.api import mail
from backend.models.rfp_entry import RFP
from backend.models.subscription import Subscription
from handlers_base import jinja_environment
from webapp2_extras.appengine.auth.models import User
from ndb import query
from backend.models import subscription
import datetime

# TODO: probably want a less personal email
default_sender = "john.sintal@gmail.com"


class EmailSender():
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

    def create_template_values(self, rfp_list, first_last_name):
        return []

    def send_rfps_to_subscribers(self):
        """
            As the function name implies, all subscribed users will receive an RFP update to their
            email accounts. By comparing an RFP's parse date to a subscription's last update date,
            we ensure dups aren't being sent out.
            
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
                rfp_list = RFP.search(sub.keyword)

                if (rfp_list and len(rfp_list) > 0):
                    logging.info("Found %d RFPs for %s with keyword %s" % (len(rfp_list), sub.username, sub.keyword))
                    #logging.info("Found %d RFPs for %s with keyword %s", (len(rfp_list), sub.username, sub.keyword))

                    #template_values = self.create_template_values(rfp_list, first_last_name)
                    template_values = {"rfps" : rfp_list,
                                       "name" : first_last_name,
                                       'search_text' : sub.keyword,
                                       'is_admin' : False}

                    subject = "RFPow! Updates: " + sub.keyword
                    self.send(subject, email, template_values)

                    # Update the last update time so we know to not send dups on next cron
                    sub.last_updated = datetime.datetime.now().date()
                    sub.put()

                else:
                    logging.info('No RFPs found for username: %s and keyword: %s' % (sub.username, sub.keyword))
            else:
                logging.info( 'No email found for username: %s  and keyword: %s' % (sub.username, sub.keyword))



    def send(self, subject="RFP Update", to="", template_values=[]):
        """
            Sends an email out based on the args given. Thin wrapper
            for Google's API.
        """

        # TODO: Don't repeat this code as it's done in the BaseHandler code.
        # TODO: I'll need to extract the rendering html method out of the BaseHandler, making
        # TODO: the parent class less heavy into an interface for this class to implement
        #template = jinja_environment.get_template('templates/email_rfp_updates.html')
        template = jinja_environment.get_template('templates/rfp_table.html')
        html = template.render(template_values)

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


