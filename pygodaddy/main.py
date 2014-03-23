"""
GoDaddy DNS Client (via pygodaddy)

Usage:
  godaddy (-h | --version)
  godaddy list {auth_args}
  godaddy find <domain> [--record-type=<t>] {auth_args}
  godaddy update <hostname> <value> [--record-type=<t>] [--new-record] {auth_args}
  godaddy delete <hostname> [--record-type=<t>] {auth_args}

Options:
  -h --help             Show this screen.
  -v --version          Show version.
  -n --new-record       With 'update' command, creates a new DNS record.
  --record-type=<t>     DNS Record Type [Default: A].
  --account=<acct>      Optional, account section name in ~/.godaddyrc config [Default: default].
  --config=<cfg>        Optional, account login config file path [Default: ~/.godaddyrc].
  --username=<user>     Optional, GoDaddy login username if not using config file.
  --password=<pass>     Optional, GoDaddy login password if not using config file.
"""

__doc__ = __doc__.format(
  auth_args='([--account=<acct>] [--config=<cfg>] | [ (--username=<user> --password=<pass>) ])'
  )

import ConfigParser
import docopt
import os.path
import pygodaddy
import sys

DEFAULT_CONFIG_PATH = os.path.expanduser('~/.godaddyrc')

class LoginConfigError(pygodaddy.GoDaddyError):
    pass

class LoginAccountNameError(LoginConfigError):
    pass

def _get_client_auth(args):
    """ finds/parses the username and password from either the args or a config file.

    :returns: a tuple of (username, password)
    """
    username, password = args['--username'], args['--password']
    if not (username and password):
        config_file_path = os.path.expanduser(args['--config'])
        if not os.path.exists(config_file_path):
            raise LoginConfigError('Login config file {0} does not exist.'.format(config_file_path))
        try:
            parser = ConfigParser.SafeConfigParser()
            parser.read(config_file_path)
            section = args['--account']
            username, password = parser.get(section, 'username'), parser.get(section, 'password')
        except ConfigParser.NoSectionError:
            raise LoginAccountNameError('Account config section {0} is not found in {1}'.format(
                repr(args['--account']),
                config_file_path
                ))
    return username, password

def _map_to_methods_and_args(client, args):
    """ maps CLI args to GoDaddyClient methods and args for separate invocation

    :param client: an instance of `pygodaddy.GoDaddyClient`
    :param args: an instance of `docopt.Dict` containing parsed args
    """
    if args['list']:
        return (client.find_domains, (), {})
    elif args['find']:
        return (
            client.find_dns_records,
            (args['<domain>'],),
            {'record_type': args['--record-type']}
            )
    elif args['update']:
        return (
            client.update_dns_record,
            (args['<hostname>'], args['<value>']),
            {'record_type': args['--record-type'], 'new': (args['--new-record'] or False)}
            )
    elif args['delete']:
        return (
            client.delete_dns_record,
            (args['<hostname>'],),
            {'record_type': args['--record-type']}
            )

def main():
    try:
        args = docopt.docopt(__doc__, version=pygodaddy.__version__)
        if args['--version']:
            print(pygodaddy.__version__)
            sys.exit(0)
        username, password = _get_client_auth(args)
        client = pygodaddy.GoDaddyClient()
        client.login(username, password)
        if not client.is_loggedin():
            sys.exit('Incorrect username/password: "{0}"/"{1}"'.format(username, password))
        method, pargs, kwargs = _map_to_methods_and_args(client, args)
        result = method(*pargs, **kwargs)
        if result is True:
            sys.exit(0) # POSIX success
        elif result is False:
            sys.exit(1) # POSIX error
        elif isinstance(result, basestring):
            print(result)
        else:
            for r in result:
                print(r)
    except pygodaddy.GoDaddyError as e:
        sys.exit(e.message)
    except docopt.DocoptLanguageError as e:
        sys.exit(e.message)

if __name__ == '__main__':
    main()
