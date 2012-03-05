import jinja2
import os
from handlers_base import user_required
import datetime
import logging
import backend.datastore as datastore
from backend.datastore import RFP
from handlers_base import BaseHandler
from google.appengine.ext.webapp import template
import google.appengine.ext.db as db

# Set up templating


from backend.parsers import MerxParser

class TopRFPSHandler(BaseHandler):
    @user_required
    def get(self):
        logging.getLogger().setLevel(logging.DEBUG)

        self.response.headers['Content-Type'] = 'text/html'
        parser = MerxParser()
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/top_rfps.html')

        # parse 10 RPFs
        rfps = parser.next()
        # parse another 10 RFPs appending results together
        rfps = rfps + parser.next()

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {"rfps": rfps,
                         "title": "Latest {0} RFP's from merx".format(len(rfps))}
        self.response.out.write(template.render(template_data))




class CreateAndQueryRFPHandler(BaseHandler):
    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/cc_rfp.html')
	template_values = {}
	self.response.out.write(template.render(template_values))

    def post(self):
        datastore.create_RFP(self.request.get('title'),
            self.request.get('description'),
            self.request.get('keywords').split(','),
            self.request.get('organization'),
            self.request.get('original_uri'),
            self.request.get('original_id'),
            datetime.datetime.now().date(),
            datetime.datetime.now().date(),
            datetime.datetime.now().date())
        self.redirect('/create-rfp/')

class KeywordResultsHandler(BaseHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/top_rfps.html')
        query = datastore.query_RFPs_by_keyword(self.request.get('keyword'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))
            # Hack since the page calls for a uri variable
            rfps[-1]['uri'] = rfps[-1]['original_uri']
            rfps[-1].pop('original_uri')

        template_data = {'rfps' : rfps,
                         'title': "Your query returned {0} RFP's".format(len(rfps))}

        self.response.out.write(template.render(template_data))


class QueryResultsHandler(BaseHandler):

    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/top_rfps.html')
        query = datastore.query_RFPs(self.request.get('query'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))
            # Hack since the page calls for a uri variable
            rfps[-1]['uri'] = rfps[-1]['original_uri']
            rfps[-1].pop('original_uri')

        template_data = {'rfps' : rfps,
                         'title': "Your query returned {0} RFP's".format(len(rfps))}

        self.response.out.write(template.render(template_data))

class HomePageHandler(BaseHandler):
    """
         Only accessible to users that are logged in, just delays a list of things for what a
         logged on user can do. In the future, it will be the dashbooard!
     """

    @user_required
    def get(self, **kwargs):
        user_session = self.auth.get_user_by_session()
        user = self.auth.store.user_model.get_by_auth_token(user_session['user_id'], user_session['token'])
        user[0].username = 'a'
        user[0].put()

        try:
            template_values = {'username':user[0].first_name,
                               'url_logout': self.auth_config['logout_url'],
                               'url_top_rfps': '/top-rfps/',
                               'url_create_query_rfps': self.request.host_url + '/create-rfp/'
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
            self.response.out.write(template.render(path, template_values))
        except (AttributeError, KeyError), e:
            return "Secure zone"
