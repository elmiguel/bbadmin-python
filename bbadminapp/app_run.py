#!/home/webapps/env/bin/python

from BbAdminApp import app
from flipflop import WSGIServer
if __name__ == '__main__':
    if app.debug:
        print("Debugging Mode: {}".format(app.config['DEBUG']))
        print("Application is running...")
        app.run()
    else:
        WSGIServer(app).run()
