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
      <datasource>MARINER_SIS</datasource>
      <datetime>2017-12-08</datetime>
   </properties>
{memberships}
</enterprise>'''

membership = '''    <membership>
        <sourcedid>
           <source>MARINER_SIS</source>
           <id>{course_id}</id>
        </sourcedid>
        <member>
           <sourcedid>
              <source>MARINER_SIS</source>
              <id>{pid}</id>
           </sourcedid>
           <idtype>{id_type}</idtype>
           <role recstatus="{recstatus}" roletype="{role}">
              <status>{status}</status>
              <userid>{user_id}</userid>
              <email>{email}</email>
              <datasource>MARINER_SIS</datasource>
           </role>
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
                        course_id=s[0],
                        pid=s[1],
                        user_id=s[2],
                        email=s[3],
                        role=s[4],
                        status=s[5],
                        id_type=s[6],
                        recstatus=s[7]
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
                recstatus=enrollment.recstatus
            )
        ]

    bb_feed = ''.join(memberships)

    with open('VC-Course-Role-Updater-Feed-GEN.xml', 'w') as o:
        o.write(xml_temp.format(memberships=bb_feed))

if __name__ == '__main__':
    opts = docopt(__doc__, version='Course Role Updater API CLI v0.0.1')
    api()

print('Job Complete!!')
