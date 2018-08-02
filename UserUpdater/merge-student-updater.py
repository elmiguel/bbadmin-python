"""MERGE Student Updater

Usage:
    merge-student-updater single OLD-ID NEW-ID FIRST-NAME LAST-NAME EMAIL PASSWORD [DSK] [options]
    merge-student-updater batch FILE [options]

Commands:
    DSK       Add a data source key. [default: MERGE_STUDENT_UPDATER]

Options:
    -h, --help      Show this screen.
    -v, --verbose   Verbose mode.

Examples:
    single with defualt DSK
        python merge-student-updater.py single S12345678 S87654321 Some Person sperson@coll.edu 12345
    single with custom DSK
        python merge-student-updater.py single S12345678 S87654321 Some Person sperson@coll.edu 12345 MY_DSK

        
"""
from docopt import docopt
import sys
import hashlib
import re
import base64
import json
from datetime import datetime

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
      <sourcedid>
         <source>{data_source_key}</source>
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
      <datasource>{data_source_key}</datasource>
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
        # print(external_person_key,user_id,firstname,lastname,email,student_id,password,data_source_key)
        people += [
            person.format(
                user_id=external_person_key,
                new_user_id=user_id,
                student_id=student_id,
                fullname=firstname + ' ' + lastname,
                first=firstname,
                last=lastname,
                email=email,
                md5='{md5}',
                password=password,
                data_source_key=data_source_key
            )
        ]

    bb_feed = ''.join(people)

    with open('./exports/MERGE-Student-Update-Feed-GEN.xml', 'w') as o:
        o.write(xml_temp.format(people=bb_feed, data_source_key=data_source_key, date=datetime.today().strftime('%Y-%m-%d')))
        # o.write(xml_temp.format(people=bb_feed))

if __name__ == '__main__':
    opts = docopt(__doc__, version='MERGE Student Updater API CLI v0.0.1')
    
    print(opts)
    
    
    data_source_key = opts['DSK'] or 'MERGE_STUDENT_UPDATER'
    
    api()
    print('Job Complete!!')
