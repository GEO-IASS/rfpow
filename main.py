import webapp2
import routes

webapp2_config = {}
webapp2_config['webapp2_extras.sessions'] = {
    'secret_key': '6023a964-ea67-4965-b8c1-8b098b87a51a',
    }

app = webapp2.WSGIApplication(config=webapp2_config)
routes.add_routes(app)
