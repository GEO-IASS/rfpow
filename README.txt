# Local development

To work on the app locally, you'll need Google's App Engine SDK:

    http://code.google.com/appengine/downloads.html

Aside from that, check out the project repo. Note that, if you use the GUI 
frontend for the SDK, it might require you to call the directory you check
out the repo into the same name as the app name, i.e. "rfpow301". 

To run the app, either add its directory in the frontend GUI, or, if you're on
a *nix OS, try using the `dev_appserver.py` script, like so:

    dev_appserver.py ~/path/to/rfpow301

For help with running the app using the frontend, refer to the GAE docs:

    http://code.google.com/appengine/docs/python/gettingstarted/helloworld.html
	
	
	
# Structure
rootdir - controller to frontend
backend - non-ui elements like parsing, db accesss, etc
template - html
