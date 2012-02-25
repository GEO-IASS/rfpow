import webapp2
import jinja2
import os
import logging

# Set up templating
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from Parsers import MerxParser

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        parser = MerxParser()

        template = jinja_environment.get_template('templates/index.html')
        rfps = parser.next()
        template_data = { "rfps": rfps }
        self.response.out.write(template.render(template_data))

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
