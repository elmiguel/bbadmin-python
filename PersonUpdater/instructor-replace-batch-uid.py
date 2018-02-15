"""Batch UID Replacer

Usage:
    instructor-replace-batch-uid.py OLD-ID NEW-ID USER-ID FIRSTNAME LASTNAME EMAIL [options]
    instructor-replace-batch-uid.py --lookup LOOKUP-TYPE LOOKUP-VALUE [options]
    instructor-replace-batch-uid.py (-h | --help)
    instructor-replace-batch-uid.py (-v | --version)

Commands:
    OLD-ID:     The current PID the is listed in either Bb or ESSQL2 or both
    NEW-ID:     The new PID that will replace the OLD-ID
    USER-ID:    The username of the account
    FIRSTNAME:  The first name of the user
    LASTNAME:   The lastname of the user
    EMAIL:      The email of the user

Options:
    -o <name>, --out-file <name>    Output file name (path/name.ext) for the current task.
                                    Defaults to: ./NEW-ID-Person.txt

    -d <dsk>, --dsk <dsk>           The data source key needed for the file. [default: ADMINTOOL]
    -s <char>, --separator <char>   Separator to use for the file field creation. [default: |]
    -h, --help                      Show this help screen.
    -L, --look
    -v, --version                   Show verions
"""
from docopt import docopt
from lookup_user import ldap_search


def main():
    old_id = args['OLD-ID']
    new_id = args['NEW-ID']
    lookup_type = args['LOOKUP-TYPE']
    lookup_value = args['LOOKUP-VALUE']
    filename = args['--out-file'] if args['--out-file'] else './%s-Person.txt' % new_id
    separator = args['--separator']
    user_id = args['USER-ID']
    firstname = args['FIRSTNAME']
    lastname = args['LASTNAME']
    email = args['EMAIL']
    dsk = args['--dsk']

    if args['--lookup']:
        users = lookup_value.split(',') if ',' in lookup_value else [lookup_value]

        for i, u in enumerate(users):
            users[i] = u.strip()

        results = ldap_search(args['LOOKUP-TYPE'], users)
        print(results)
    else:
        # one-shot user feed file generation
        with open(filename, 'w') as o:
            headers = ['external_person_key', 'user_id', 'firstname', 'lastname',
                       'email', 'new_external_person_key', 'data_source_key']
            data = [old_id, user_id, firstname, lastname, email, new_id, dsk]
            o.write(separator.join(headers))
            o.write('\n' + separator.join(data))

if __name__ == '__main__':
    args = docopt(__doc__, version='Batch UID Replacer v0.0.1')
    main()
