from google.appengine.api import mail
from handlers_base import jinja_environment


class EmailSender():
    """
        EmailSender is responsible for gathering RFP data for each user who has subscribed to
        email updates, then sending that data via email.
    """

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

