# -*- coding: utf-8 -*-

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
        rfps = rfp_entry.RFP.all().fetch(limit=20)

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {"rfps": rfps,
                "title": "Latest {0} RFP's from merx".format(len(rfps))}
        self.show_rendered_html('templates/home.html', template_data)

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
        self.show_rendered_html('templates/cc_rfp.html', template_values)



class KeywordResultsHandler(BaseHandler):
    ''' Once a desired keyword is obtained from the user, a page consisting
    of every RFPs stored in the database will be displayed with template
    keyword_results.html'''

    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        query = rfp_entry.query_RFPs_by_keyword(self.request.get('keyword'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))

        template_data = {'rfps' : rfps,
                'title': "Your query returned {0} RFP's".format(len(rfps))}
        self.show_rendered_html('templates/keyword_results.html', template_data)



class QueryResultsHandler(BaseHandler):

    @user_required
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        query = rfp_entry.query_RFPs(self.request.get('query'))

        rfps  = []

        for r in query:
            rfps.append(db.to_dict(r))

        template_data = {'rfps' : rfps,
                'title': "Your query returned {0} RFP's".format(len(rfps))}
        self.show_rendered_html('templates/keyword_results.html', template_data)

class ListKeywordsHandler(BaseHandler):
    ''' List every keyword stored in database for use to select, once selected, 
    a result page consisting of every RFP with this keyword will be displayed.'''

    @user_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        keywords = rfp_entry.query_Keywords(self.request.get('keyword'))

        template_data = {'keywords' : keywords }
        self.show_rendered_html('templates/list_keywords.html', template_data)


class HomePageHandler(BaseHandler):
    """
         Only accessible to users that are logged in, just delays a list of things for what a
         logged on user can do. In the future, it will be the dashbooard!
     """

    @user_required
    def get(self, template_data=None):

        # normally, we generate
        if template_data is None:
            rfps = rfp_entry.RFP.all().order( 'publish_date' ).fetch(25)
            template_data = { 
                'rfps': rfps,
                'is_admin': self.is_user_admin()
            }

        # now stash results into a dict and use it in the top_rfps.html template
        self.show_rendered_html( 'templates/home.html', template_data )

class RFPList(BaseHandler):
    """Return table of RFPs, sorted by given column and starting at given offset.""" 
    @user_required
    def get(self, format):
        sort_by = self.request.get( 'order' ).strip()
        start_offset = self.request.get( 'offset' ).strip()

        if start_offset is not '':
            try: 
                start_offset = int( start_offset )
            except ValueError:
                start_offset = 0
        else:
            start_offset = 0

        if sort_by == '':
            sort_by = 'publish_date'

        query = rfp_entry.RFP.all().order( sort_by )
        rfps = query.fetch( offset=start_offset, limit=25 )

        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {"rfps": rfps}
        
        # render HTML
        if format is '':
            handler = HomePageHandler( request=self.request, response=self.response )
            return handler.get( template_data )
        # AJAX-friendly output
        elif format == '.comet':
            self.show_rendered_html( 'templates/rfp_table.html', template_data)

class RFPDetails(BaseHandler):
    """Return details for given RFP ID"""

    @user_required
    def get(self, rfp_id):
        rfp = rfp_entry.RFP.get_by_id( int(rfp_id) )

        # no such RFP exists
        if rfp is None:
            self.response.set_status(400)
            self.response.out.write( 'No such RFP exists' )
            return

        # otherwise, return it
        template_data = { 'rfp': rfp }
        self.show_rendered_html( 'templates/rfp_details.html', template_data )

class RFPSearch(BaseHandler):
    """Return table of search results for given search query. 
    
       Used by AJAX handler for modal dialogue.    
    """

    @user_required
    def get(self, search_query, format ):
        rfps = rfp_entry.RFP.search( search_query )
        template_data = { 
            'rfps': rfps,
            'search_text': search_query,
            'is_admin': self.is_user_admin()
        }

        # no such RFP exists
        if rfps is None:
            self.response.set_status(400)
            self.response.out.write( 'No such RFP exists' )

        # return either just the results table, or the whole page
        if format is '':
            handler = HomePageHandler( request=self.request, response=self.response )
            return handler.get( template_data )

        # AJAX-friendly output
        elif format == '.comet':
            self.show_rendered_html( 'templates/rfp_table.html', template_data)
