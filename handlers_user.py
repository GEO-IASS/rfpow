# -*- coding: utf-8 -*-

"""
	All user controls are located here (login, create and logout)
"""

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from handlers_base import BaseHandler, HTMLRenderer
from handlers_base import user_required
from backend.models.rfpow_user import RFPowUser
from backend.models.subscription import Subscription


class LoginHandler(BaseHandler, HTMLRenderer):
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
        self.show_rendered_html('templates/login.html', template_values)

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
            self.redirect('/')
        except (InvalidAuthIdError, InvalidPasswordError), e:
            self.show_login("Bad username or password. Try again.")


class UserFormBaseHandler(BaseHandler, HTMLRenderer):
    """
        Returns a simple HTML form for creating/editing a user.
    """

    def show_register(self, err_msg="", info_msg=""):
		user = None
		username = self.get_username()
		subscriptions = None

		if username is not None:
			# grab all user's subscriptions
			subscriptions = Subscription.all().filter( 'username =', username ).fetch(1000)

		template_values = {
				'action': self.request.url,
				'err_msg': err_msg, "user": user,
				"username": username,
				'info_msg': info_msg,
				'subscriptions' : subscriptions
				}
		self.show_rendered_html('templates/user_info_form.html', template_values)


class CreateUserHandler(UserFormBaseHandler):
    def get(self):
        self.show_register()

    def create_insert_user(self, rfpow_user):
        """ Creates and inserts a new user, returns a the user object.

        As the UI changes and the need for more user info increases, this list
        will grow
        """
        user = self.auth.store.user_model.create_user(
            rfpow_user.username,
            username=rfpow_user.username,
            password_raw=rfpow_user.password,
            first_name=rfpow_user.first_name,
            last_name=rfpow_user.last_name,
            email=rfpow_user.email,
            cc_number=rfpow_user.cc_number,
            name_on_cc=rfpow_user.name_on_cc,
            expiry_date_month=rfpow_user.expiry_date_month,
            expiry_date_year=rfpow_user.expiry_date_year,
            is_admin=rfpow_user.username == 'admin',
            is_active=False
        )
        return user

    def post(self):
        """
              Get what the user posted in the form
        """
        rfpow_user = RFPowUser(self.request.POST)

        user = self.create_insert_user(rfpow_user)

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


class EditUserHandler(UserFormBaseHandler):
    """
        Made sense to keep this handler in the handlers_user even though
        it's secured and part of the main UI.
    """

    @user_required
    def get(self):
        self.show_register()

    @user_required
    def post(self):
        """
              Get what the user posted in the form
        """
        rfpow_user = RFPowUser(self.request.POST)
        user = self.curr_user()[0]

        if not user:
            self.show_register(err_msg="Error with username");
        else:
            rfpow_user.update(user)
            try:
                self.show_register(info_msg="Ok, we updated your account info!")
            except (AttributeError, KeyError), e:
                self.abort(403)


class LogoutHandler(BaseHandler, HTMLRenderer):
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



