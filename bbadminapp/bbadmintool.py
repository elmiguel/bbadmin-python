import datetime
from flask import current_app
from flask_ldapconn import LDAPConn
from flask import _app_ctx_stack as stack
import httplib2
import re
from ldap3 import SUBTREE
from json import JSONEncoder


class MyEncoder(JSONEncoder):
    def default(self, obj):
        # return obj.__dict__
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(MyEncoder, self).default(obj)

class BbAdminTool(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
            self.ldap = LDAPConn(app)
        self.isXML = False
        self.ldap_results = []
        self.bb_results = []
        self.reference_code = ""

    def init_app(self, app):
        app.config.setdefault('BBA_USER', None)
        app.config.setdefault('BBA_PASS', None)
        app.config.setdefault('BBA_XML_USER_PROD', None)
        app.config.setdefault('BBA_XML_USER_DEV', None)
        app.config.setdefault('BBA_XML_PASS', None)
        app.config.setdefault('BBA_TIMER', 5.0)
        app.config.setdefault('BBA_BASE_URL', None)
        app.config.setdefault('BBA_XML_BASE_URL_PROD', None)
        app.config.setdefault('BBA_XML_BASE_URL_DEV', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE_ASSOC', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE_CAT', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE_MEM', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE_CAT_MEM', None)
        app.config.setdefault('BBA_ENTRYPOINT_COURSE_STAND_ASSOC', None)
        app.config.setdefault('BBA_ENTRYPOINT_HIERARCHY_NODE', None)
        app.config.setdefault('BBA_ENTRYPOINT_OBSERVER_ASSOC', None)
        app.config.setdefault('BBA_ENTRYPOINT_ORGANIZATION', None)
        app.config.setdefault('BBA_ENTRYPOINT_ORGANIZATION_ASSOC', None)
        app.config.setdefault('BBA_ENTRYPOINT_ORGANIZATION_CAT', None)
        app.config.setdefault('BBA_ENTRYPOINT_ORGANIZATION_CAT_MEM', None)
        app.config.setdefault('BBA_ENTRYPOINT_PERSON', None)
        app.config.setdefault('BBA_ENTRYPOINT_TERM', None)
        app.config.setdefault('BBA_ENTRYPOINT_USER_ASSOC', None)
        app.config.setdefault('BBA_ENTRYPOINT_USER_SEC_INST_ROLE', None)
        app.config.setdefault('BBA_DATA_SOURCES', None)
        app.config.setdefault('BBA_LDAP_BASEDN', None)
        app.config.setdefault('BBA_LDAP_ATTRIBUTES', None)
        app.config.setdefault('BBA_FEEDFILE_SEPARATOR', ",")
        app.config.setdefault('BBA_FEEDFILE_PERSON_LDAP', None)
        app.config.setdefault('BBA_FEEDFILE_PERSON_NO_LDAP', None)
        app.config.setdefault('BBA_FEEDFILE_COURSE', None)
        app.config.setdefault('BBA_FEEDFILE_COURSE_ENROLLMENT', None)
        app.config.setdefault('BBA_FEEDFILE_ORGANIZATION_ENROLLMENT', None)

        app.extensions['bb_admin_tool'] = self

        app.teardown_appcontext(self.teardown)

    @staticmethod
    def teardown(exception):
        ctx = stack.top
        if hasattr(ctx, 'bb_admin_tool'):
            ctx.bb_admin_tool.unbind()

    @property
    def connection(self, url, data, xml=False, env='prod'):
        if not xml:
            username = current_app.config['BBA_USER']
            password = current_app.config['BBA_PASS']
        else:
            self.isXML = True
            password = current_app.config['BBA_XML_PASS']
            if env == 'dev':
                username = current_app.config['BBA_XML_USER_DEV']
            else:
                username = current_app.config['BBA_XML_USER_PROD']


        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'bb_admin_tool'):
                ctx.bb_admin_tool = self.post_data(username, password, url, data)
            return ctx.bb_admin_tool

    @staticmethod
    def lower_params(params):
        if len(params) is 0:
            return None
        return [p.lower() for p in params]

    @staticmethod
    def title_params(params):
        if len(params) is 0:
            return None
        return [p.title() for p in params]

    def post_data(self, username, password, url, data):
        h = httplib2.Http()
        h.add_credentials(username, password)
        content_type = "text/plain"

        if self.isXML:
            content_type = "text/xml"
        resp, content = h.request(url, "POST", body=data, headers={"content-type": content_type})
        print(resp)
        print(content)
        reference_code = re.search(r"(\w{32})", str(content)).group(0)
        self.reference_code = reference_code
        return reference_code

    def bb_search(self, params=None):
        if params is not None and params != []:
            #do bb open db search
            pass
        pass

    def ldap_search(self, search_type=None, params=['no_name'], first_names=['no_name'], last_names=['no_name']):
        """
            search_type: username | firstname | lastname | pid | first_last
                username: uses params
                firstname: tries first_names first if none, then params
                lastname: tries last_names first if none, then params
                pid: uses params
                first_last: uses first_names and last_names to generate names
        """

        if search_type is not None:
            names = []
            if search_type == 'first_last':
                first_names = self.title_params(first_names)
                last_names = self.title_params(last_names)
                for first in first_names:
                    for last in last_names:
                        names += ['(&(givenName={first})(sn={last}))'.format(first=first, last=last)]

            search_filters = dict(
                username='(&(objectClass=user)(|{seq}))'.format(
                    seq=''.join(['(sAMAccountName=%s)' % name for name in self.lower_params(params)])),

                firstname='(&(objectClass=user)(|{seq}))'.format(
                    seq=''.join(['(givenName=%s)' % name for name in self.title_params(first_names or params)])),

                lastname='(&(objectClass=user)(|{seq}))'.format(
                    seq=''.join(['(sn=%s)' % name for name in self.title_params(last_names or params)])),

                pid='(&(objectClass=user)(|{seq}))'.format(
                    seq=''.join(['(employeeID=%s)' % pid for pid in params])),

                first_last='(&(objectClass=user)(|{seq}))'.format(
                    seq=''.join(names)
                )

            )

            # print(search_filters['first_last'])
            # return None
            ldapc = self.ldap.connection
            basedn = current_app.config['BBA_LDAP_BASEDN']
            search_filter = search_filters[search_type]
            attributes = current_app.config['BBA_LDAP_ATTRIBUTES']

            ldapc.search(basedn, search_filter, SUBTREE, attributes=attributes)
            response = ldapc.response

            #  response holds two keys: attributes and raw_attributes(bytes)
            self.ldap_results = MyEncoder().encode([dict(r['attributes']) for r in response])
            return self.ldap_results
