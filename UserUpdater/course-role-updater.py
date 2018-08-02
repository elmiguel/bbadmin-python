"""Course Role Update

Usage:
    course-role-updater single COURSE-ID PID USER-ID EMAIL ROLE-ID STATUS ID-TYPE RECSTATUS [options]
    course-role-updater batch FILE [options]

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
from datetime import datetime
# CLASSES


class Membership:

    def __init__(self, course_id, pid, user_id,  email, role_id, status, id_type, recstatus):
        self.course_id = course_id
        self.user_id = user_id
        self.pid = pid
        self.id_type = id_type
        self.role_id = role_id
        self.recstatus = recstatus
        self.status = status
        self.email = email

# GLOBALS
md5 = hashlib.md5()

xml_temp = '''<?xml version="1.0" encoding="UTF-8"?>
<enterprise xmlns="http://imsglobal.org/IMS_EPv1p1">
   <properties>
      <datasource>{data_source_key}</datasource>
      <datetime>{date}</datetime>
   </properties>
{memberships}
</enterprise>'''

membership = '''    <membership>
        <sourcedid>
           <source>{data_source_key}</source>
           <id>{c{date}/id>
        </sourcedid>
        <member>
           <sourcedid>
              <source>{data_source_key}</source>
              <{date}id>
           </sourcedid>
           <idtype>{id_type}</idtype>
           <role recstatus="{recstatus}" roletype="{role}">
              <status>{status}</status>
              <userid>{user_id}</userid>
              <email>{email}</email>
              <datasource>{data_source_key}</datasource>
     {date}le>
        </member>
    </membership>'''


def process_batch(file_path):
    members = []
    with open(file_path) as f:
        data = f.read().split('\n')
        for m in data[1:]:
            if m != '':
                m = m.split(',')
                members += [
                    Membership(
                        course_id=m[0],
                        pid=m[1],
                        user_id=m[2],
                        email=m[3],
                        role_id=m[4],
                        status=m[5],
                        id_type=m[6],
                        recstatus=m[7]
                    )
                ]
    return members


def api():
    if opts['--verbose']:
        print(opts)
    if opts['batch']:
        enrollments = process_batch(opts['FILE'])
    else:
        enrollments = [Membership(
            opts['COURSE-ID'],
            opts['PID'],
            opts['USER-ID'],
            opts['EMAIL'],
            opts['ROLE-ID'],
            opts['STATUS'],
            opts['ID-TYPE'],
            opts['RECSTATUS'],

        )]

    memberships = []
    # print(people[0].old_id)
    for enrollment in enrollments:
        memberships += [
            membership.format(
                course_id=enrollment.course_id,
                pid=enrollment.pid,
                user_id=enrollment.user_id,
                email=enrollment.email,
                role=enrollment.role_id,
                status=enrollment.status,
                id_type=enrollment.id_type,
                recstatus=enrollment.recstatus,
                data_source_key=data_source_key
            )
        ]

    bb_feed = ''.join(memberships)

    with open('VC-Course-Role-Updater-Feed-GEN.xml', 'w') as o:
        o.write(xml_temp.format(memberships=bb_feed, data_source_key=data_source_key, date=datetime.today().strftime('%Y-%m-%d')))

if __name__ == '__main__':
    opts = docopt(__doc__, version='Course Role Updater API CLI v0.0.1')
    api()
    data_source_key='MY_DSK'

print('Job Complete!!')
