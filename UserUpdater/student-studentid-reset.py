import hashlib
import httplib2
from sqlalchemy.engine import create_engine
import re
import base64
import sys
from datetime import datetime
curl = '''
curl -k -w %{http_code} -H "Content-Type:text/xml" -u '<SIS_XML_INT_USER>:<SIS_XML_INT_PASS>' --data-binary @FTIC-Student-Update-Feed-GEN.xml https://irsc.blackboard.com/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint
'''


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

md5 = hashlib.md5()

xml_temp = '''<?xml version="1.0" encoding="UTF-8"?>
<enterprise xmlns="http://imsglobal.org/IMS_EPv1p1">
   <properties>
      <datasource>{data_source_key}</datasource>
      <datetime>{date}</datetime>
   </properties>
{people}
</enterprise>'''

person = '''
   <person>
      <sourcedid>
         <source>{data_source_key}</source>
         <id>{user_id}</id>
      </sourcedid>
      <userid>{user_id}</userid>
      <name>
         <fn>{fullname}</fn>
         <n>
            <family>{last}</family>
            <given>{first}</given>
         </n>
      </name>
      <email>{email}</email>
      <datasource>{data_source_key}</datasource>
      <extension>
        <ns0:WEBCREDENTIALS xmlns:ns0="http://www.webct.com/IMS">{md5}{password}</ns0:WEBCREDENTIALS>
        <ns1:transactionType xmlns:ns1="http://www.irsc.edu">STDNT</ns1:transactionType>
        <ns2:studentId xmlns:ns2="http://www.irsc.edu">{student_id}</ns2:studentId>
      </extension>
   </person>'''

debug = False
bbEngine = create_engine(
    'oracle+cx_oracle://<OPENDB_USER>:<OPENDB_PASS>@<OPENDB_IP>:<POR>/<INSTANCE>', echo=debug)
bbConn = bbEngine.connect()
bbResult = bbConn.execute(
    "SELECT * FROM BBLEARN.USERS U WHERE U.STUDENT_ID LIKE '(%'")
bbConn.close()
bb_students = "'" + "','".join([r.batch_uid for r in bbResult]) + "'"
# [print(r.batch_uid) for r in bbResult]
# for r in bbResult:
#     print(r.batch_uid)
# print(bb_students)
# sys.exit(1)

essqlEngine = create_engine('mssql+pyodbc://<SQL_USER>:<SQL_PADS@<SQL_INSTANCE>', echo=debug)
esConn = essqlEngine.connect()
sql = """
...select statement to collect from interal SQL Server a data set based on curreent Bb records set status: bb_students...
""".format(bb_students)

# print(sql)

ftic = esConn.execute(sql).fetchall()
# count = 0
# for f in ftic:
#     if count >= 10:
#         break
#     print(f)
#     count += 1

esConn.close()

people = []

ftic_re = re.compile(r"\(\w+\)-", re.IGNORECASE)

# some clean up as sql is not respecting the last record query
_ftic = {}
for s in ftic:
    _ftic.update({
        s.external_person_key: {
            "user_id": s.user_id,
            "fullname": s.firstname + ' ' + s.lastname,
            "firstname": s.firstname,
            "lastname": s.lastname,
            "password": hashlib.md5(s.passwd.encode('utf-16le')).hexdigest().upper(),
            "email": s.email,
            "student_id": s.student_id,
            "data_source_key": s.data_source_key,
        }
    })
# for k, v in _ftic.items():
#     print(k, v)
#
# sys.exit(1)
for k, v in _ftic.items():
    external_person_key = k
    user_id = v['user_id']
    fullname = v['fullname']
    firstname = v['firstname']
    lastname = v['lastname']
    password = v['password']
    email = v['email']
    student_id = v['student_id']
    data_source_key = v['data_source_key']
    people += [
        person.format(
            user_id=user_id,
            student_id=student_id,
            fullname=fullname,
            first=firstname,
            last=lastname,
            email=email,
            md5='{md5}',
            password=password
        )
    ]

bb_feed = ''.join(people)
# print('Bb Results:', bbResult.count(), 'ESSQL2 Results:', ftic.count(),
# 'People Processed:', len(people))
print('People Processed: ', len(people))
# print(bb_feed)
# sys.exit(1)
with open('Student-StudentId-Update-Feed-RESET.xml', 'w') as o:
    o.write(xml_temp.format(people=bb_feed, data_source_key='MY_DSK', date=datetime.today().strftime('%Y-%m-%d')))

# send_bb_feed_file(bb_feed)

print('Job Complete!!')
