# -*- coding: utf-8 -*-

"""
	All user controls are located here (login, create and logout)
"""

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import os
from google.appengine.ext.webapp import template
from handlers_base import BaseHandler



class LoginHandler(BaseHandler):
    def get(self):
        url = self.request.host_url + '/create-user/'
        url_linktext = 'New User?'
        template_values = {'action': self.request.url, 'url': url, 'url_linktext': url_linktext}
        path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
        self.response.out.write(template.render(path, template_values))


    def post(self):
        """
             Get what the user and pass posted in the form
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
            self.redirect('/login')
            # return "Login error. Try again: <a href='%s'>Login</a>" % (self.auth_config['login_url'])


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
              Get what the user posted in the form
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



