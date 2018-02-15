import hashlib
import httplib2
from sqlalchemy.engine import create_engine
import re
import base64
import sys

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
    h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    creds = bytes(bb_user + ':' + bb_pass, 'ascii')
    auth = str(base64.encodestring(creds))[2:-3]
    # print(auth)
    # h.add_credentials(bb_user, bb_pass)
    resp, content = h.request(bb_endpoint,
                              "POST",
                              body=bb_feed,
                              headers={
                                  "Authorization": "Basic %s" % auth,
                                  "Content-Type": "text/xml"
                              })
    # print(h.__repr__)
    reference_code = re.search(r"(\w{32})", str(content)).group(0)
    print('\nReceived reference code:', reference_code)
    return reference_code

md5 = hashlib.md5()

xml_temp = '''<?xml version="1.0" encoding="UTF-8"?>
<enterprise xmlns="http://imsglobal.org/IMS_EPv1p1">
   <properties>
      <datasource>MARINER_SIS</datasource>
      <datetime>2018-01-23</datetime>
   </properties>
{people}
</enterprise>'''

person = '''
   <person>
      <sourcedid>
         <source>MARINER_SIS</source>
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
      <datasource>MARINER_SIS</datasource>
      <extension>
        <ns0:WEBCREDENTIALS xmlns:ns0="http://www.webct.com/IMS">{md5}{password}</ns0:WEBCREDENTIALS>
        <ns1:transactionType xmlns:ns1="http://www.irsc.edu">STDNT</ns1:transactionType>
        <ns2:studentId xmlns:ns2="http://www.irsc.edu">{student_id}</ns2:studentId>
      </extension>
   </person>'''

debug = False
essqlEngine = create_engine('mssql+pyodbc://<SQL_USER>:<SQL_PASS>@<SQL_INSTANCE>', echo=debug)
esConn = essqlEngine.connect()
sql = """
select  
    et.user_id external_person_key,
    et.user_id,
    first_name firstname,
    last_name lastname,
    password passwd,
    email_inst as email,
    replace(
        replace('('+ isnull(convert(varchar(2), ed.cohort),'')
        + isnull(ed.pgrad, '')
        + ')-' + et.user_id, ' ', '')
        ,'()-', '')
    as student_id,
    'MARINER_SIS' data_source_key
from elearning_trans et,
     elearning_designators ed,
    (select
         user_id,
        max(record_seq) as max_record
     from elearning_trans
     where user_id !='TBA'
     and user_id not like '[0-9]%'
     group by user_id
     ) ms
where et.user_id=ed.studentid
and ms.max_record=et.record_seq
"""

# print(sql)

ftic = esConn.execute(sql)

people = []

for student in ftic:
    external_person_key = student.external_person_key
    user_id = student.user_id
    firstname = student.firstname
    lastname = student.lastname
    password = hashlib.md5(student.passwd.encode('utf-16le')).hexdigest().upper()
    email = student.email
    student_id = student.student_id
    data_source_key = student.data_source_key
    people += [
        person.format(
            user_id=user_id,
            student_id=student_id,
            fullname=firstname + ' ' + lastname,
            first=firstname,
            last=lastname,
            email=email,
            md5='{md5}',
            password=password
        )
    ]

esConn.close()

bb_feed = ''.join(people)

# with open('Student-Update-Feed-GEN-New.xml', 'w') as o:
#     o.write(xml_temp.format(people=bb_feed))

send_bb_feed_file(xml_temp.format(people=bb_feed))
print('People Processed:', len(people))
print('Job Complete!!')
