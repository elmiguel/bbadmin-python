import os
basedir = os.path.abspath(os.path.dirname(__file__))

# App Settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'bba_app.db')
SQLALCHEMY_TRACK_MODIFICATIONS=True
ESSQL2_DATABASE_URI = 'mssql+pyodbc://<SQL_USER>:<SQL_PASS>@<SQL_INSTANCE>'
APPLICATION_ROOT = basedir
TEMPLATE_FOLDER = os.path.join(basedir, '/templates')
SECRET_KEY = '<SECRET_KEY>' # of your choosing
DEBUG = True

# LDAP Settings
LDAP_SERVER = 'ldap://<YOUR_LDAP_SERVER>'
LDAP_PORT = 389
LDAP_BINDDN = r'<DOMAIN>\<USER>'
LDAP_SECRET = '<LDAP_USER_PASS>'
LDAP_TIMEOUT = 10
LDAP_USE_TLS = False

# Database Common
DATETIME = "%Y-%m-%d %H:%M:%S"
DATE = "%Y-%m-%d"

# Blackboard SIS Integration Settings
# LDAP base dn is used for this current app context, find a way to include it to the LDAPConn class
# then when the Bb class it initialized it will accept a LDAPConn class object and read from there.
BBA_OPENDB_URL = 'oracle+cx_oracle://<OPENDB_USER>:<OPENDB_PASS>@<OPENDB_IP>:<POR>/<INSTANCE>'
BBA_SCHEMA = 'BBLEARN'
BBA_TIMER = 5.0
BBA_LDAP_BASEDN = '<LDAP_BASEDN>'
BBA_LDAP_ATTRIBUTES = ['sn', 'givenName', 'employeeID', 'mail', 'cn', 'displayName', 'distinguishedName',
                       'whenChanged', 'whenCreated', 'uSNChanged', 'uSNCreated', 'description', 'memberOf',
                       'badPwdCount']
BBA_USER = "<SIS_INTEGRATION_USER>"
BBA_PASS = "<SIS_INTEGRATION_PASS>"
BBA_FEEDFILE_SEPARATOR = "|"
BBA_BASE_URL = "https://<BB_INSTANCE>/webapps/bb-data-integration-flatfile-BBLEARN/endpoint"
BBA_ENTRYPOINT_COURSE = BBA_BASE_URL + "/course"
BBA_ENTRYPOINT_COURSE_ASSOC = BBA_BASE_URL + "/courseassociation"
BBA_ENTRYPOINT_COURSE_CAT = BBA_BASE_URL + "/coursecategory"
BBA_ENTRYPOINT_COURSE_CAT_MEM = BBA_BASE_URL + "/coursecategorymembership"
BBA_ENTRYPOINT_COURSE_MEM = BBA_BASE_URL + "/membership"
BBA_ENTRYPOINT_COURSE_STAND_ASSOC = BBA_BASE_URL + "/standardsassociation"
BBA_ENTRYPOINT_HIERARCHY_NODE = BBA_BASE_URL + "/node"
BBA_ENTRYPOINT_OBSERVER_ASSOC = BBA_BASE_URL + "/associateobserver"
BBA_ENTRYPOINT_ORGANIZATION = BBA_BASE_URL + "/organization"
BBA_ENTRYPOINT_ORGANIZATION_MEM = BBA_BASE_URL + "/organizationmembership"
BBA_ENTRYPOINT_ORGANIZATION_ASSOC = BBA_BASE_URL + "/organizationassociation"
BBA_ENTRYPOINT_ORGANIZATION_CAT = BBA_BASE_URL + "/organizationcategory"
BBA_ENTRYPOINT_ORGANIZATION_CAT_MEM = BBA_BASE_URL + "/organizationcategorymembership"
BBA_ENTRYPOINT_PERSON = BBA_BASE_URL + "/person"
BBA_ENTRYPOINT_TERM = BBA_BASE_URL + "/term"
BBA_ENTRYPOINT_USER_ASSOC = BBA_BASE_URL + "/userassociation"
BBA_ENTRYPOINT_USER_SEC_INST_ROLE = BBA_BASE_URL + "/secondaryinstrole"
BBA_DATA_SOURCES = ['ADMINTOOL', 'LDAP_Faculty', 'MARINER_SIS', 'DEV_Shells', 'PRAC_Shells']
BBA_FEEDFILE_PERSON_LDAP = BBA_FEEDFILE_SEPARATOR.join([
    "external_person_key",
    "user_id",
    "firstname",
    "lastname",
    "email",
    "data_source_key",
    "institution_role",
    "system_role"])
BBA_FEEDFILE_PERSON_NO_LDAP = BBA_FEEDFILE_SEPARATOR.join([
    "external_person_key",
    "user_id",
    "firstname",
    "lastname",
    "email",
    "data_source_key",
    "institution_role",
    "system_role"])
BBA_FEEDFILE_COURSE = BBA_FEEDFILE_SEPARATOR.join([
    "external_course_key",
    "course_id",
    "course_name",
    "data_source_key",
    "template_course_key"])
BBA_FEEDFILE_ORGANIZATION = BBA_FEEDFILE_SEPARATOR.join([
    "external_organization_key",
    "organization_id",
    "organization_name",
    "data_source_key",
    "template_organization_key"])
BBA_FEEDFILE_COURSE_ENROLLMENT = BBA_FEEDFILE_SEPARATOR.join([
    "external_course_key",
    "external_person_key",
    "role",
    "row_status",
    "available_ind",
    "data_source_key"])
BBA_FEEDFILE_ORGANIZATION_ENROLLMENT = BBA_FEEDFILE_SEPARATOR.join([
    "external_organization_key",
    "external_person_key",
    "role",
    "row_status",
    "available_ind",
    "data_source_key"])
BBA_OPENDB_SYSTEM_ROLES = {
    'N': 'None',
    'C': 'Course Administrator',
    'U': 'Guest',
    'BB_LE_ADMIN': 'Learning Environment Administrator',
    'O': 'Observer',
    'BB_OUTCOMES_ADMIN': 'Outcomes Administrator',
    'R': 'Support',
    'Z': 'System Administrator',
    'H': 'System Support',
    'BB_TEMPLATES_ADMIN': 'Templates Administrator',
    'A': 'User Administrator'
}

BBA_XML_BASE_URL_PROD = "https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint"
BBA_XML_BASE_URL_DEV = "https://<BB_INSTANCE>/webapps/bb-data-integration-ims-xml-BBLEARN/endpoint"
BBA_XML_USER_PROD = '<SIS_XML_INTEGRATION_USER>'
BBA_XML_USER_DEV = '<SIS_XML_INTEGRATION_USER>'
BBA_XML_PASS = '<SIS_XML_INTEGRATION_PASS>'