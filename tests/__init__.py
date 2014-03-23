"""
GoDaddy DNS Client (via pygodaddy)

Usage:
  godaddy (-h | --version)
  godaddy list
  godaddy find <domain> --record-type=<t> {auth_args}
  godaddy update <hostname> <value> --record-type=<t> [--new-record] {auth_args}
  godaddy delete <hostname> --record-type=<t> {auth_args}

Options:
  -h --help      Show this screen.
  --version      Show version.
  --record-type  DNS Record Type [Default: 'A']
  --new-record   With 'update' command, creates a new DNS record
  --account      Optional, account section name in ~/.godaddyrc config [Default: 'default']
  --username     Optional, GoDaddy login username if not using ~/.godaddyrc config
  --password     Optional, GoDaddy login password if not using ~/.godaddyrc config
"""

__doc__ = __doc__.format(
  auth_args='([--account <acct>] | [ --username=<user> --password=<pass> ])'
  )
