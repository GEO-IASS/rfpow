# -*- coding: utf-8 -*-

"""
	A real simple app for using webapp2 with auth and session.

	It just covers the basics. Creating a user, login, logout and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py

"""

import webapp2
from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import os
from google.appengine.ext.webapp import template

def user_required(handler):
    """
         Decorator for checking if there's a user associated with the current session.
         Will also fail if there's no session present.
     """

    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            # If handler has no login_url specified invoke a 403 error
            try:
                self.redirect(self.auth_config['login_url'], abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class BaseHandler(webapp2.RequestHandler):
    """
         BaseHandler for all requests

         Holds the auth and session properties so they are reachable for all requests
     """

    def dispatch(self):
        """
              Save the sessions for preservation across requests
          """
        try:
            response = super(BaseHandler, self).dispatch()
            #self.response.write(response)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def auth_config(self):
        """
              Dict to hold urls for login/logout
          """
        return {
            'login_url': self.uri_for('login'),
            'logout_url': self.uri_for('logout')
        }


class LoginHandler(BaseHandler):
    def get(self):
        url = self.request.host_url + '/create-user/'
        url_linktext = 'New User?'
        template_values = {'action': self.request.url, 'url': url, 'url_linktext': url_linktext}
        path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
        self.response.out.write(template.render(path, template_values))


    def post(self):
        """
            username: Get the username from POST dict
            password: Get the password from POST dict
        """
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        remember_me = True if self.request.POST.get('remember_me') == 'on' else False
        # Try to login user with password
        # Raises InvalidAuthIdError if user is not found
        # Raises InvalidPasswordError if provided password doesn't match with specified user
        try:
            self.auth.get_user_by_password(username, password, remember=remember_me)
            self.redirect('/secure')
        except (InvalidAuthIdError, InvalidPasswordError), e:
            # Returns error message to self.response.write in the BaseHandler.dispatcher
            # Currently no message is attached to the exceptions
            # return e
            return "Login error. Try again: <a href='%s'>Login</a>" % (self.auth_config['login_url'])


class CreateUserHandler(BaseHandler):
    def get(self):
        """
              Returns a simple HTML form for create a new user
          """
        template_values = {'action': self.request.url}
        path = os.path.join(os.path.dirname(__file__), 'templates/register.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        """
              username: Get the username from POST dict
              password: Get the password from POST dict
          """
        str_username = self.request.POST.get('username')
        str_password = self.request.POST.get('password')
        str_first_name = self.request.POST.get('first_name')
        str_last_name = self.request.POST.get('last_name')
        str_cc_number = self.request.POST.get('cc_number')
        str_name_on_cc = self.request.POST.get('name_on_cc')
        str_expiry_date = self.request.POST.get('expiry_date')
        str_keywords = self.request.POST.get('keywords')
        list_keywords = []
        for x in str_keywords.split(','):
            list_keywords.append(x.strip())


        # As the UI changes and the need for more user info increases, this list
        # will grow
        user = self.auth.store.user_model.create_user(
            str_username,
            password_raw=str_password,
            first_name=str_first_name,
            last_name=str_last_name,
            cc_number=str_cc_number,
            name_on_cc=str_name_on_cc,
            expiry_date=str_expiry_date,
            keywords=list_keywords,
            is_admin=False,
            is_active=False
        )
        if not user[0]: #user is a tuple
            return 'Create user error: %s' % str(user) # Error message
        else:
            # User is created, let's try redirecting to login page
            try:
                self.redirect(self.auth_config['login_url'], abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)


class LogoutHandler(BaseHandler):
    """
         Destroy user session and redirect to login
     """

    def get(self):
        self.auth.unset_session()
        # User is logged out, let's try redirecting to login page
        try:
            self.redirect(self.auth_config['login_url'])
        except (AttributeError, KeyError), e:
            return "User is logged out"


class SecureRequestHandler(BaseHandler):
    """
         Only accessible to users that are logged in
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
