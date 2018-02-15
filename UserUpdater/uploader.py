# Supplied by Blackboard Tech....

#import hashlib
import httplib2
import re
import base64
import sys
import argparse

parser = argparse.ArgumentParser("Process SIS Feed File")
parser.add_argument("file", nargs=None, help="feed file path")
args = parser.parse_args()

def upload_feed_file(feed_file):
	print "Starting upload..."
	end_point = "https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint"
	bb_user = "<SIS_INT_USER>"
	bb_pass = "<SIS_INT_PASS>"

	# needed to add the following due to CERTIFICATE_VERIFY_FAILED
	h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
	auth = base64.encodestring( bb_user + ':' + bb_pass )
	#print (auth)

	# POST request
	resp, content = h.request( end_point, "POST", body=feed_file, headers={ "Content-Type": "text/xml", "Authorization": "Basic " + auth } )
	
	return ( re.search(r"(\w{32})", str(content)).group(0) )


# passing in binary data for our feed file
try:
	with open( args.file, 'rb' ) as f:
		print ("Received Reference Code:", upload_feed_file( f.read() ) )
		print ("Finished")
		f.close()
except IOError:
	print ( "feed file doesn't exist, exting..." )
	sys.exit(1)