import hashlib
import base64
import sys
import csv
md5 = hashlib.md5()

xml_temp = '''<?xml version="1.0" encoding="UTF-8"?>
<enterprise xmlns="http://imsglobal.org/IMS_EPv1p1">
   <properties>
      <datasource>MARINER_SIS</datasource>
      <datetime>2017-01-19</datetime>
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


people = []

with open('./StudentID-Cohort-Leftovers.csv') as f:
    _ftic = csv.DictReader(f, skipinitialspace=True, quotechar='`', delimiter='|')

    for v in _ftic:
        external_person_key = v['external_person_key']
        user_id = v['user_id']
        fullname = v['firstname'] + ' ' + v['lastname']
        firstname = v['firstname']
        lastname = v['lastname']
        password = v['passwd']
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
# print(people)
# sys.exit(1)

bb_feed = ''.join(people)
# print('Bb Results:', bbResult.count(), 'ESSQL2 Results:', ftic.count(),
# 'People Processed:', len(people))
print('People Processed: ', len(people))
# print(bb_feed)
# sys.exit(1)
with open('Student-StudentId-Update-Feed-GEN.xml', 'w') as o:
    o.write(xml_temp.format(people=bb_feed))

# send_bb_feed_file(bb_feed)

print('Job Complete!!')
