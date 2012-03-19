import jinja2
import os
from handlers_base import user_required
import datetime
import logging
import backend.models.rfp_entry as rfp_entry
from backend.models.rfp_entry import RFP
from handlers_base import BaseHandler
from google.appengine.ext.webapp import template
import google.appengine.ext.db as db
from backend.parsers import MerxParser



class TopRFPSHandler(BaseHandler):
    '''This will query and display the top 10 RFPs stored in the database.'''

    @user_required
    def get(self):
        logging.getLogger().setLevel(logging.DEBUG)

        self.response.headers['Content-Type'] = 'text/html'
        jinja_environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/home.html')

        rfps = rfp_entry.RFP.all().fetch(limit=20)

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {"rfps": rfps,
                "title": "Latest {0} RFP's from merx".format(len(rfps))}
        self.response.out.write(template.render(template_data))

class CreateRFPHandler(BaseHandler):

    @user_required
    def post(self):
        rfp_entry.create_RFP(self.request.get('title'),
                self.request.get('description'),
                self.request.get('keywords').split(','),
                self.request.get('organization'),
                self.request.get('original_uri'),
                self.request.get('original_id'),
                datetime.datetime.now().date(),
                datetime.datetime.now().date(),
                datetime.datetime.now().date())
        self.redirect('/admin/')


class QueryRFPHandler(BaseHandler):
    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/cc_rfp.html')
        template_values = {}
        self.response.out.write(template.render(template_values))


class KeywordResultsHandler(BaseHandler):
    ''' Once a desired keyword is obtained from the user, a page consisting
    of every RFPs stored in the database will be displayed with template
    keyword_results.html'''

    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/keyword_results.html')
        query = rfp_entry.query_RFPs_by_keyword(self.request.get('keyword'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))

        template_data = {'rfps' : rfps,
                'title': "Your query returned {0} RFP's".format(len(rfps))}

        self.response.out.write(template.render(template_data))


class QueryResultsHandler(BaseHandler):

    @user_required
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/keyword_results.html')
        query = rfp_entry.query_RFPs(self.request.get('query'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))

        template_data = {'rfps' : rfps,
                'title': "Your query returned {0} RFP's".format(len(rfps))}

        self.response.out.write(template.render(template_data))

class ListKeywordsHandler(BaseHandler):
    ''' List every keyword stored in database for use to select, once selected, 
    a result page consisting of every RFP with this keyword will be displayed.'''

    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/list_keywords.html')
        keywords = rfp_entry.query_Keywords(self.request.get('keyword'))

        template_data = {'keywords' : keywords }

        self.response.out.write(template.render(template_data))

class HomePageHandler(BaseHandler):
    """
         Only accessible to users that are logged in, just delays a list of things for what a
         logged on user can do. In the future, it will be the dashbooard!
     """

    @user_required
    def get(self, **kwargs):
        self.response.headers['Content-Type'] = 'text/html'
        jinja_environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/home.html')

        rfps = rfp_entry.RFP.all().fetch(100)

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {"rfps": rfps}
        self.response.out.write(template.render(template_data))

class RFPDetails(BaseHandler):
    """Return details for given RFP ID"""

    @user_required
    def get(self, rfp_id):
        self.response.headers['Content-Type'] = 'text/html'
        jinja_environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/rfp_details.html')

        rfp = rfp_entry.RFP.get_by_id( int(rfp_id) )

        # no such RFP exists
        if rfp is None:
            self.response.set_status(400)
            self.response.out.write( 'No such RFP exists' )
            return

        # otherwise, return it
        template_data = { 'rfp': rfp }
        self.response.out.write(template.render(template_data))

class RFPSearch(BaseHandler):
    """Return table of search results for given search query. 
    
       Used by AJAX handler for modal dialogue.    
    """

    @user_required
    def get(self, search_query):
        self.response.headers['Content-Type'] = 'text/html'
        jinja_environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('templates/rfp_table.html')

        rfps = rfp_entry.RFP.search( search_query )

        # no such RFP exists
        if rfps is None:
            self.response.set_status(400)
            self.response.out.write( 'No such RFP exists' )
            return

        # otherwise, return it
        template_data = { 'rfps': rfps }
        self.response.out.write(template.render(template_data))
