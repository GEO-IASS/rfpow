import webapp2
from webapp2_extras import auth
from webapp2_extras import sessions
import os
import jinja2
import lib.jinja_filters as jinja_filters

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
jinja_environment.filters['nl2pbr'] = jinja_filters.do_nl2pbr

def user_required(handler):
    """
         Decorator for checking if there's a user associated with the current session.
         Will also fail if there's no session present.

         Use this for all functions that need to be secured. This will prevent unauthorized
         access to our RFP services.
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

class HTMLRenderer():
    """
        Handles all the rendering of html to the client along with its template values
    """

    def get_rendered_html(self, filename="", template_args=[]):
        template = jinja_environment.get_template(filename)
        return template.render(template_args)

    def show_rendered_html(self, filename="", template_args=[]):
        """
            Displays html to the client using the template given by the location
            in filename, along with the arguments from template_args.
        """

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.get_rendered_html(filename, template_args))


class BaseHandler(webapp2.RequestHandler, HTMLRenderer):
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

    def curr_user(self):
        """
            Return the current user if there is one, else
            return None
        """

        user_session = self.auth.get_user_by_session()
        if (user_session is None):
            return None
        else:
            db_user = self.auth.store.user_model.get_by_auth_token(user_session['user_id'], user_session['token'])
            return db_user

    def get_username(self):
        """
            Return the username of the currently logged user. Return None if no user is present
            in the session.
        """

        if self.curr_user():
            username = self.curr_user()[0].username
            if username and len(username) > 0:
                return username
            else:
                return None
        else:
            return None

    def is_user_admin(self):
        """
            Return true if current signed in user is an admin, else false. This will return false
            if no user has signed in the webapp.
        """

        return self.curr_user() != None and self.curr_user()[0].is_admin


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

