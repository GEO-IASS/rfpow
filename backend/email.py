from google.appengine.api import mail
from backend.models.rfp_entry import RFP
from backend.models.subscription import Subscription
from handlers_base import jinja_environment
from webapp2_extras.appengine.auth.models import User
from ndb import query
from backend.models import subscription


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

    def test(self):
        subscription.create_subscription("john3", "French")


        subs = Subscription.all()
        for sub in subs:

            # Grab what user info, add first, last name later
            email = self.get_email(sub.username)

            # Ensure the the sub's username is associated with an actual account
            # by checking if the email exists.
            if (email):
                first_last_name = self.get_first_last_name(sub.username)

                # Query RFPs based on this subscription's keyword
                rfp_list = RFP.search(sub.keyword)
                fea = 4





    def send(self, sender, subject, to, template_values):
        """
            Sends an email out based on the args given. Thin wrapper
            for Google's API.
        """
        template = jinja_environment.get_template('templates/email_rfp_updates.html')
        html = template.render(template_values)

        message = mail.EmailMessage()
        message.sender = sender
        message.subject = subject
        message.to = to
        message.html = html
        message.send()

