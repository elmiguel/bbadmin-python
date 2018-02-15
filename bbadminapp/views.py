import re
import sys
import ssl
import hashlib
import requests
# from flask.ext.login import login_required, current_user, logout_user, login_user
from flask_login import login_required, current_user, logout_user, login_user
# from flask.ext.restless.views import ProcessingException
from flask_restless import ProcessingException
# from flask.ext.wtf.form import Form
from flask_wtf import Form
from flask.helpers import flash, url_for, send_from_directory
from flask.json import jsonify
from flask.templating import render_template
from flask import redirect, request
import httplib2
import pyodbc
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from wtforms.fields.core import StringField
from wtforms.fields.simple import PasswordField, SubmitField
from BbAdminApp import app, login_manager, bb
from bbadmintool import MyEncoder
from models import *
from bba_config import ESSQL2_DATABASE_URI
import base64
from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_company():
    return {'company': '<YOUR_COMPANY_NAME>'}


def auth_func(*args, **kw):
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)


def allow_control_headers(response):
    # * allows all access, good for development, bad for prod....unless you want it that way.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


def preprocessor(search_params=None, **kw):
    # This checks if the preprocessor function is being called before a
    # request that does not have search parameters.
    if search_params is None:
        return
    # Create the filter you wish to add; in this case, we include only
    # instances with ``id`` not equal to 1.
    filt = dict(name='id', op='neq', val=1)
    # Check if there are any filters there already.
    if 'filters' not in search_params:
        search_params['filters'] = []
    # *Append* your filter to the list of filters.
    search_params['filters'].append(filt)


def get_postprocessor(result=None, search_params=None, **kw):
    if result:
        result.update(
            {"draw": 1,
             "recordsTotal": result['num_results'],
             "recordsFiltered": len(result['objects']),
             "data": result['objects']})
        del result['objects']
        del result['num_results']

        # app.logger.debug(result)
    else:
        app.logger.debug("get_postprocessor() being called but not passing the actual results...")


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


# @app.route('/test')
# def index_test():
#     # bb.search(self, search_type=None, params=None, first_names=None, last_names=None):
#     # when using search_type='username', params is used
#
#     # bb.ldap_search('username', params=['mbechtel', 'jlhart'])
#     # bb.ldap_search('pid', params=['xxxxx', 'yyyyy'])
#     # bb.ldap_search('first_last', first_names=['michael', 'jonathan'], last_names=['bechtel', 'hart'])
#     # return 'Hello World!<br>{}'.format(bb.ldap_results)
#     return render_template('index.html')


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('sync_user.html')


@app.route('/sync_user', methods=['GET'])
@login_required
def sync_user():
    return render_template('sync_user.html')


@app.route('/ldap/user/<path:cn>', methods=['GET'])
@login_required
def ldap_user_search_by_cn(cn):
    print(cn)
    if cn == 'bbafacilitator':
        user = {
            "data": MyEncoder().encode(
                [
                    {
                        "whenChanged": "2015-07-05T22:36:32+00:00",
                        "givenName": "BBADMIN",
                        "distinguishedName": "CN=bbafacilitator,OU=MainCampus,OU=College,DC=irsc,DC=edu",
                        "description": ["TEST - TEST bbafacilitator"],
                        "displayName": "BBADMIN FACILITATOR",
                        "whenCreated": "2008-08-09T17:40:03+00:00",
                        "uSNChanged": 99999999,
                        "mail": "noreply@irsc.edu",
                        "sn": "FACILITATOR",
                        "memberOf": [],
                        "employeeID": "bbafacilitator",
                        "badPwdCount": 0,
                        "cn": "bbafacilitator",
                        "uSNCreated": 99999
                    }
                ]
            )
        }
    else:
        user = {"data": bb.ldap_search('username', [cn])}

    return jsonify(user)


@app.route('/bb/user', methods=['GET', 'POST'])
@login_required
def sync_user_to_bb():
    rv = {
        "person": "This is a Test Response!",
        "enrollments": [],
        "shells": [],
    }

    if request.method == 'POST':
        print(request.json)
        data = request.json

        bb_feed = app.config["BBA_FEEDFILE_PERSON_LDAP"]
        bb_feed += "\n{pkey}|{uid}|{fn}|{ln}|{em}|{dsk}|{ir}|{sr}".format(
            pkey=data["pid"],
            uid=data["username"],
            fn=data["firstname"],
            ln=data["lastname"],
            em=data["email"],
            dsk=data["data_source_key"],
            ir=data["institution_role"],
            sr=data["system_role"]
        )
        entrypoint = app.config["BBA_ENTRYPOINT_PERSON"] + '/store'

        rv["person"] = send_bb_feed_file(entrypoint, bb_feed)

        # if workday, generate org enrollment
        if data["workday"]:
            print("workday set to True")
            data.update({
                'external_organization_key': 'ORG-WORKDAY-TRAINING',
                'role': 'S',
                'row_status': 'enabled',
                'available_ind': 'Y'
            })
            rv['enrollments'] += [bb_enroll('organization', data)]
        # if tech training, generate org enrollment
        if data["tech_training"]:
            print("tech training set to True")
            data.update({
                'external_organization_key': 'IT-ORG',
                'role': 'S',
                'row_status': 'enabled',
                'available_ind': 'Y'
            })
            rv['enrollments'] += [bb_enroll('organization', data)]

        # if bb_essentials, generate course enrollment
        if data["bb_essentials"]:
            print("bb_essentials set to True")
            data.update({
                'external_course_key': 'VC-Blackboard_Essentials',
                'role': 'S',
                'row_status': 'enabled',
                'available_ind': 'Y'
            })
            rv['enrollments'] += [bb_enroll('course', data)]

        # if prac_gc, create practice grade center and enrollment
        if data["prac_gc"]:
            print("prac_gc set to True")
            # first create the course
            data.update({
                'external_course_key': "PRAC-GC-{user}".format(user=data["username".lower()]),
                'course_id': "PRAC-GC-{user}".format(user=data["username".lower()]),
                'course_name': "Practice - Grade Center - {user}".format(user=data["username".lower()]),
                'role': 'F',
                'row_status': 'enabled',
                'available_ind': 'Y',
                'template_course_key': 'TRAIN0009-ONLINE'
            })
            rv['shells'] += [bb_create_shell('course', data)]

            # then create the enrollment
            rv['enrollments'] += [bb_enroll('course', data)]

        # if training, create practice grade center and enrollment
        if data["training"]:
            print("training set to True")
            # first create the course
            data.update({
                'external_course_key': "TRAIN-{user}".format(user=data["username".lower()]),
                'course_id': "TRAIN-{user}".format(user=data["username".lower()]),
                'course_name': "Training - {user}".format(user=data["username".lower()]),
                'role': 'P',
                'row_status': 'enabled',
                'available_ind': 'Y',
                'template_course_key': 'IRSC-DEVSHELL-TEMPLATE'
            })

            rv['shells'] += [bb_create_shell('course', data)]

            # then create the enrollment
            rv['enrollments'] += [bb_enroll('course', data)]

    return jsonify(rv)


def bb_enroll(etype, data):
    print("bb_enroll:", data)

    bb_feed = app.config["BBA_FEEDFILE_{etype}_ENROLLMENT".format(etype=etype.upper())]
    bb_feed += "\n{etk}|{epk}|{r}|{rs}|{ai}|{dsk}".format(
        etk=data["external_{etype}_key".format(etype=etype)],
        epk=data["pid"],
        r=data["role"],
        rs=data["row_status"],
        ai=data["available_ind"],
        dsk=data["data_source_key"]
    )

    entrypoint = app.config["BBA_ENTRYPOINT_{etype}_MEM".format(etype=etype.upper())] + '/store'

    reference_code = send_bb_feed_file(entrypoint, bb_feed)

    return reference_code

def bb_create_shell(etype, data):
    """
    :type etype: string = course | organization
    :type data: object = response.json
    """
    bb_feed = app.config["BBA_FEEDFILE_{etype}".format(etype=etype.upper())]
    bb_feed += "\n{etk}|{tk}|{tn}|{dsk}|{ttk}".format(
        etk=data["external_{etype}_key".format(etype=etype)],
        tk=data["{etype}_id".format(etype=etype)],
        tn=data["{etype}_name".format(etype=etype)],
        dsk=data["data_source_key"],
        ttk=data["template_{etype}_key".format(etype=etype)]
    )

    entrypoint = app.config["BBA_ENTRYPOINT_{etype}".format(etype=etype.upper())] + '/store'

    reference_code = send_bb_feed_file(entrypoint, bb_feed)

    return reference_code


def send_bb_feed_file(entrypoint, bb_feed):
    print('Sending bb_feed to:', entrypoint)
    # post the data to bb
    # h = httplib2.Http()

    # h.add_credentials(app.config["BBA_USER"], app.config["BBA_PASS"])
    # resp, content = h.request(entrypoint,
    #                           "POST",
    #                           body=bb_feed,
    #                           headers={"content-type": "text/plain"})
    # print(content)
    # reference_code = re.search(r"(\w{32})", str(content)).group(0)

    r = requests.post(
        entrypoint, 
        data=bb_feed,
        headers={"content-type": "text/plain"},
        auth=requests.auth.HTTPBasicAuth(
            app.config["BBA_USER"], 
            app.config["BBA_PASS"]), 
        verify=False)
    reference_code = re.search(r"(\w{32})", str(r.content)).group(0)
    print('Received reference code:', reference_code)
    return reference_code


def send_bb_xml_feed_file(entrypoint, bb_feed):
    print('Sending bb_feed to:', entrypoint)
    # print(bb_feed)
    print(app.config["BBA_XML_USER_PROD"], app.config["BBA_XML_PASS"])
    # post the data to bb
    h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)

    h.add_credentials(app.config["BBA_XML_USER_PROD"], app.config["BBA_XML_PASS"])
    # creds = bytes(app.config["BBA_XML_USER_PROD"] + ':' + app.config["BBA_XML_PASS"], 'ascii')
    # auth = str(base64.encodestring(creds))[2:-3]
    resp, content = h.request(entrypoint,
                              "POST",
                              body=bb_feed,
                              headers={
                                #   "Authorization": "Basic %s" % auth,
                                  "content-type": "text/xml"
                              })
    # print(content)
    # r = requests.post(
    #     entrypoint, 
    #     data=bb_feed,
    #     headers={"content-type": "text/xml"},
    #     auth=requests.auth.HTTPBasicAuth(
    #         app.config["BBA_XML_USER"], 
    #         app.config["BBA_XML_PASS"]),
    #     verify=False,
    #     timeout=5000)
    # print(r.content)
    reference_code = re.search(r"(\w{32})", str(content)).group(0)
    print('\nReceived reference code:', reference_code)
    return reference_code



@app.route('/sync_ftic', methods=['GET'])
@login_required
def sync_ftic():
    essql = create_engine(ESSQL2_DATABASE_URI, echo=True)
    esConn = essql.connect()
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
    ftic = esConn.execute(sql)
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
            <source>{data_source_key}</source>
            <id>{external_person_key}</id>
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
                external_person_key=external_person_key,
                user_id=user_id,
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

    esConn.close()
    # print(bb_feed)
    bb_feed = ''.join(people)
    bb_feed = xml_temp.format(people=bb_feed)
    reference_code = send_bb_xml_feed_file(app.config["BBA_XML_BASE_URL_PROD"], bb_feed)
    # essql_conn.close()
    return render_template('sync_ftic.html', reference_code=reference_code)


@app.route('/dbtables', methods=['GET'])
@login_required
def dbtables():
    return render_template('dbtables.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You successfully logged out! Goodbye! :)')
    return redirect('login')


@app.errorhandler(401)
def not_authenticated(error):
    if not current_user.is_authenticated:
        flash('You are not currently logged in, please login.', 'error')
        return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit() or request.method == 'POST':
        username, password = form.username.data, form.password.data
        print(username, password)

        # first get user, then verify
        user = db.session.query(User).filter(User.username == username).first()

        if user:
            if user.verify_password(password=password):
                login_user(user, remember=True)
                flash('Logged in successfully', 'success')

                # next_page = request.args.get('next')
                # print(next_page)

                return redirect(url_for('index'))
            else:
                flash('Username or password invalid', 'error')
        else:
            flash('Username or password invalid', 'error')
    return render_template('login.html', form=form)


# MODELS
class LoginForm(Form):
    username = StringField('username')
    password = PasswordField('password')
    submit = SubmitField('submit')



