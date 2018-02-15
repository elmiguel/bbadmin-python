"""MERGE Student Updater

Usage:
    merge-student-updater single OLD-ID NEW-ID FIRST-NAME LAST-NAME EMAIL PASSWORD [options]
    merge-student-updater batch FILE [options]

Options:
    -h, --help                      Show this screen.
    -v, --verbose                   Verbose mode.

"""
from docopt import docopt
import sys
import hashlib
import re
import base64
import json

# CLASSES
class Person:
    def __init__(self, old_id, new_id, first_name, last_name, email, password):
        self.old_id = old_id
        self.new_id = new_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

# GLOBALS
md5 = hashlib.md5()

xml_temp = '''<?xml version="1.0" encoding="UTF-8"?>
<enterprise xmlns="http://imsglobal.org/IMS_EPv1p1">
   <properties>
      <datasource>MARINER_SIS</datasource>
      <datetime>2017-04-19</datetime>
   </properties>
{people}
</enterprise>'''

person = '''
   <person>
      <sourcedid>
         <source>MARINER_SIS</source>
         <id>{user_id}</id>
      </sourcedid>
      <sourcedid>
         <source>MARINER_SIS</source>
         <id>{new_user_id}</id>
      </sourcedid>
      <userid>{new_user_id}</userid>
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

def process_batch(file_path):
    students = []
    with open(file_path) as f:
        data = f.read().split('\n')
        for s in data[1:]:
            if s != '':
                s = s.split(',')
                students += [
                    Person(
                        old_id=s[0],
                        new_id=s[1],
                        first_name=s[2],
                        last_name=s[3],
                        email=s[4],
                        password=s[5]
                    )
                ]
    return students

def api():
    if opts['--verbose']:
        print(opts)
    if opts['batch']:
        merges = process_batch(opts['FILE'])
    else:
        merges = [Person(
            opts['OLD-ID'],
            opts['NEW-ID'],
            opts['FIRST-NAME'],
            opts['LAST-NAME'],
            opts['EMAIL'],
            opts['PASSWORD'],
            )]

    people = []
    # print(people[0].old_id)
    for student in merges:
        external_person_key = student.old_id
        user_id = student.new_id
        firstname = student.first_name.title()
        lastname = student.last_name.title()
        password = hashlib.md5(student.password.encode('utf-16le')).hexdigest().upper()
        email = student.email
        student_id = student.new_id
        data_source_key = 'MARINER_SIS'
        # print(external_person_key,user_id,firstname,lastname,email,student_id,password,data_source_key)
        people += [
            person.format(
                user_id=external_person_key,
                new_user_id=user_id,
                student_id=user_id,
                fullname=firstname + ' ' + lastname,
                first=firstname,
                last=lastname,
                email=email,
                md5='{md5}',
                password=password
            )
        ]

    bb_feed = ''.join(people)

    with open('MERGE-Student-Update-Feed-GEN.xml', 'w') as o:
        o.write(xml_temp.format(people=bb_feed))

if __name__ == '__main__':
    opts = docopt(__doc__, version='MERGE Student Updater API CLI v0.0.1')
    api()

print('Job Complete!!')
