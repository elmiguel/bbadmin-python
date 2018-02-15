from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
from config import LDAP_BINDDN, LDAP_PORT, LDAP_SECRET, LDAP_SERVER, LDAP_TIMEOUT, LDAP_USE_TLS, BBA_LDAP_BASEDN, BBA_LDAP_ATTRIBUTES
from json import JSONEncoder, dumps, loads
import datetime


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


def lower_params(params):
    if len(params) is 0:
        return None
    return [p.lower() for p in params]


def title_params(params):
    if len(params) is 0:
        return None
    return [p.title() for p in params]


def ldap_search(search_type=None, params=['no_name'], first_names=None, last_names=None):
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
            first_names = title_params(first_names)
            last_names = title_params(last_names)
            for first in first_names:
                for last in last_names:
                    names += ['(&(givenName={first})(sn={last}))'.format(first=first, last=last)]

        search_filters = dict(
            username='(&(objectClass=user)(|{seq}))'.format(
                seq=''.join(['(sAMAccountName=%s)' % name for name in lower_params(params)])),

            firstname='(&(objectClass=user)(|{seq}))'.format(
                seq=''.join(['(givenName=%s)' % name for name in title_params(first_names or params)])),

            lastname='(&(objectClass=user)(|{seq}))'.format(
                seq=''.join(['(sn=%s)' % name for name in title_params(last_names or params)])),

            pid='(&(objectClass=user)(|{seq}))'.format(
                seq=''.join(['(employeeID=%s)' % pid for pid in params])),

            first_last='(&(objectClass=user)(|{seq}))'.format(
                seq=''.join(names)
            )
        )

        server = Server(host=LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        conn = Connection(server=server, user=LDAP_BINDDN, password=LDAP_SECRET,
                          authentication=NTLM, auto_bind=True)
        conn.search(BBA_LDAP_BASEDN, search_filters[
                    search_type], SUBTREE, attributes=BBA_LDAP_ATTRIBUTES)

        return loads(MyEncoder().encode([dict(r['attributes']) for r in conn.response]))
