import hashlib
import httplib2
import re
import base64
import sys

curl = '''
curl -k -w %{http_code} -H "Content-Type:text/xml" -u '<SIS_XML_INT_USER>:<SIS_XML_INT_PASS>' --data-binary @FTIC-Student-Update-Feed-GEN.xml https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint
'''
filename = {
    "reset": "./Student-Update-Feed-RESET.xml",
    "gen": "./Student-Update-Feed-GEN-New.xml",
    "reset:test": "./Student-Update-Feed-RESET-Test.xml",
    "gen:test": "./Student-Update-Feed-GEN-New-Test.xml",
}

def send_bb_feed_file(bb_feed):
    # prod
    # bb_endpoint='https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint'
    # bb_user='<PROD_USER>'

    # staging
    bb_endpoint = 'https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint'
    bb_user = '<DEV_USER>'

    bb_pass = '<PASS>'

    print('Sending bb_feed to:', bb_endpoint)
    # post the data to bb
    # httplib2.debuglevel = 1
    h = httplib2.Http()
    creds = bytes(bb_user + ':' + bb_pass, 'ascii')
    auth = str(base64.encodestring(creds))[2:-3]
    # print(auth)
    # h.add_credentials(bb_user, bb_pass)
    resp, content = h.request(bb_endpoint,
                              "POST",
                              body=xml_temp.format(people=bb_feed),
                              headers={
                                  "Authorization": "Basic %s" % auth,
                                  "Content-Type": "text/html",
                                  "Accept": "*/*"
                              })
    # print(h.__repr__)
    reference_code = re.search(r"(\w{32})", str(content)).group(0)
    print('\nReceived reference code:', reference_code)
    return reference_code

with open(filename['reset:test'], 'r') as f:
    print(send_bb_feed_file(f.read()))
print('Job Complete!!')
