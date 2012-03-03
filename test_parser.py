import webapp2
import jinja2
import os
import logging

# Set up templating
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from backend.parsers import MerxParser

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        parser = MerxParser()
        template_data = {}

        template = jinja_environment.get_template('templates/top_rfps.html')

        try:
            # parse 10 RPFs
            rfps = parser.next()
            # parse another 10 RFPs appending results together
            rfps = rfps + parser.next()

            # now stash results into a dict and use it in the index.html template
            template_data[ "rfps" ] = rfps 
        except IOError as e:
            template_data[ "error" ] = "Couldn't connect to Merx"

        self.response.out.write(template.render(template_data))

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/toprfps', MainPage)],
                              debug=True)
