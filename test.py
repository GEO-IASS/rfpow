import webapp2
import jinja2
import os

# Set up templating
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from Parsers import MerxParser

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'

      template = jinja_environment.get_template('templates/index.html')
      template_data = { "rfps": MerxParser.get_latest() }
      self.response.out.write(template.render(template_data))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
