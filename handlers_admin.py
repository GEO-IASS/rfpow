import webapp2
import jinja2
import os
import logging
from backend.scheduled import ScheduledParse

class AdminParser(webapp2.RequestHandler):
    """Controller for the parser section of the admin panel"""

    def get(self, status=None):
        self.response.headers['Content-Type'] = 'text/html'
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/admin_parsers.html')

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {}
        
        if status is not None: 
            template_data['status'] = status
        self.response.out.write(template.render(template_data))

    def post(self):
        """Used to set parser settings and trigger parsers"""
        ignore_duplicates = self.request.get('ignore_duplicates')
        start_id = self.request.get('start_id')
        stop_on_dupe = self.request.get('stop_on_dupe')
        limit = self.request.get('parse_limit')

        (parsed, new) = ScheduledParse.parse_merx( 
                ignore_duplicates is not '',
                (start_id is not "") and start_id or None,
                stop_on_dupe is not '',
                (limit is not "") and int(limit.strip()) or None )

        self.get( '%d RFPs parsed, %d new stored. See logs.' % (parsed, new) )


app = webapp2.WSGIApplication(
        [('/admin', AdminParser)],
        debug=True,
        config= {
            'webapp2_extras.sessions':
            { 'secret_key': '6023a964-ea67-4965-b8c1-8b098b87a51a' }
        })
