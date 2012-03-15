# -*- coding: utf-8 -*-

"""
	All user controls are located here (login, create and logout)
"""

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import os
from google.appengine.ext.webapp import template
from handlers_base import BaseHandler
from backend.RFPowUser import RFPowUser


class LoginHandler(BaseHandler):
    """
         Show a form for the user to login. If the there's an empty string error
         msg for error_msg, display it the user.
    """

    def show_login(self, err_msg="", info_msg=None):
        template_values = {
            'action': self.request.url,
            'err_msg': err_msg,
            'info_msg': info_msg
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
        self.response.out.write(template.render(path, template_values))

    def get(self, error_msg=""):
        self.show_login()

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
            self.show_login("Bad username or password. Try again.")


class CreateUserHandler(BaseHandler):
    """
        Returns a simple HTML form for creating a new user. Show err_msg if
        not empty (logic is in html)
    """

    def show_register(self, err_msg=""):
        template_values = {'action': self.request.url, 'err_msg': err_msg}
        path = os.path.join(os.path.dirname(__file__), 'templates/register.html')
        self.response.out.write(template.render(path, template_values))

    def get(self):
        self.show_register()


    def post(self):
        """
              Get what the user posted in the form
          """
#        str_username = self.request.POST.get('username')
#        str_password = self.request.POST.get('password')
#        str_first_name = self.request.POST.get('first_name')
#        str_last_name = self.request.POST.get('last_name')
#        str_cc_number = self.request.POST.get('cc_number')
#        str_name_on_cc = self.request.POST.get('name_on_cc')
#        str_expiry_date_month = self.request.POST.get('expiry_date_month')
#        str_expiry_date_year = self.request.POST.get('expiry_date_year')
#        str_expiry_date = str_expiry_date_month + "," + str_expiry_date_year
#        str_email = self.request.POST.get('email')
        # str_keywords = self.request.POST.get('keywords')
        #        list_keywords = []
        #        for x in str_keywords.split(','):
        #            list_keywords.append(x.strip())

        rfpow_user = RFPowUser(self.request.POST)

        # As the UI changes and the need for more user info increases, this list
        # will grow
        user = self.auth.store.user_model.create_user(
            rfpow_user.username,
            password_raw=rfpow_user.password,
            first_name=rfpow_user.first_name,
            last_name=rfpow_user.last_name,
            email=rfpow_user.email,
            cc_number=rfpow_user.cc_number,
            name_on_cc=rfpow_user.name_on_cc,
            expiry_date=rfpow_user.expiry_date,
            is_admin=False,
            is_active=False
        )
        if not user[0]:
            self.show_register("User already exists, try again");
        else:
            # User is created, let user know they're good to log in
            try:
                h = LoginHandler()
                h.initialize(self.request, self.response)
                h.show_login(
                    info_msg="Hooray, you're registered! Log in below."
                )
            except (AttributeError, KeyError), e:
                self.abort(403)


class EditUserHandler(BaseHandler):
    def show_register(self, err_msg=""):
        template_values = {'action': self.request.url, 'err_msg': err_msg}
        path = os.path.join(os.path.dirname(__file__), 'templates/register.html')
        self.response.out.write(template.render(path, template_values))

    def get(self):
        self.show_register("COW")

    def post(self):
        """
              Get what the user posted in the form
          """
        rfpow_user = RFPowUser(self.request.POST)
        user_session = self.auth.get_user_by_session()
        db_user = self.auth.store.user_model.get_by_auth_token(user_session['user_id'], user_session['token'])


        if not db_user[0]:
            #return 'Create user error: %s' % str(user) # Error message
            self.show_register("Error with username");
        else:
            rfpow_user.update(db_user)
            try:
                self.show_register("Success changing account info!")
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



