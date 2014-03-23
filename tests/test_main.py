import docopt
import os
import pygodaddy
import pygodaddy.main as main
import tempfile
import unittest

class TestArgMapping(unittest.TestCase):
    """
    Tests that CLI args are properly mapped to GoDaddyClient method calls
    """
    def setUp(self):
        self.client = pygodaddy.GoDaddyClient()

    def _test(self, arg_string, expect_method, expect_pargs, expect_kwargs):
        args = docopt.docopt(main.__doc__, argv=arg_string)
        method, pargs, kwargs = main._map_to_methods_and_args(self.client, args)
        self.assertEqual(expect_method, method)
        self.assertEqual(expect_pargs, pargs)
        self.assertEqual(expect_kwargs, kwargs)

    def test_list(self):
        self._test('list', self.client.find_domains, (), {})

    def test_find(self):
        self._test(
            'find example.com',
            self.client.find_dns_records,
            ('example.com',),
            {'record_type': 'A'}
            )
        self._test(
            'find example.com --record-type=C',
            self.client.find_dns_records,
            ('example.com',),
            {'record_type': 'C'}
            )

    def test_update(self):
        self._test(
            'update foo.example.com 192.168.1.2',
            self.client.update_dns_record, ('foo.example.com', '192.168.1.2'),
            {'record_type': 'A', 'new': False}
            )
        self._test(
            'update foo.example.com 192.168.1.2 --record-type=C',
            self.client.update_dns_record, ('foo.example.com', '192.168.1.2'),
            {'record_type': 'C', 'new': False}
            )
        self._test(
            'update foo.example.com 192.168.1.2 --record-type=C --new-record',
            self.client.update_dns_record, ('foo.example.com', '192.168.1.2'),
            {'record_type': 'C', 'new': True}
            )
        self._test(
            'update foo.example.com 192.168.1.2 -n',
            self.client.update_dns_record, ('foo.example.com', '192.168.1.2'),
            {'record_type': 'A', 'new': True}
            )

    def test_delete(self):
        self._test(
            'delete foo.example.com',
            self.client.delete_dns_record,
            ('foo.example.com',),
            {'record_type': 'A'}
            )
        self._test(
            'delete foo.example.com --record-type=C',
            self.client.delete_dns_record,
            ('foo.example.com',),
            {'record_type': 'C'}
            )


class TestClientAuth(unittest.TestCase):

    def _test(self, arg_string, expect_username, expect_password):
        args = docopt.docopt(main.__doc__, argv=arg_string)
        u, p = main._get_client_auth(args)
        self.assertEqual((expect_username, expect_password), (u, p))

    def test_client_auth(self):
        self._test('list --username=foo --password=bar', 'foo', 'bar')

    def test_client_config_default_account_name(self):
        _, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('\n'.join(['[default]', 'username = alibaba', 'password = opensesame']))
        self._test('list --config={0}'.format(path), 'alibaba', 'opensesame')
        os.remove(path)

    def test_client_config_account_name_match(self):
        _, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('\n'.join(['[personal]', 'username = alibaba', 'password = opensesame']))
            f.write('\n')
            f.write('\n'.join(['[work]', 'username = milton', 'password = redstapler']))
        self._test('list --config={0} --account=personal'.format(path), 'alibaba', 'opensesame')
        self._test('list --config={0} --account=work'.format(path), 'milton', 'redstapler')
        os.remove(path)

    def test_client_config_account_name_mismatch(self):
        _, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('\n'.join(['[personal]', 'username = alibaba', 'password = opensesame']))
        self.assertRaises(
            main.LoginAccountNameError,
            self._test,
            'list --config={0} --account=work'.format(path), # acct name mismatch
            'alibaba', 'opensesame'
            )

    def test_auth_invalids(self):
        self.assertRaises(
            docopt.DocoptExit,
            self._test,
            'list --username=foo', # missing password
            'foo', 'bar'
            )
        self.assertRaises(
            docopt.DocoptExit,
            self._test,
            'list --password=bar', # missing username
            'foo', 'bar'
            )
        self.assertRaises(
            docopt.DocoptExit,
            self._test,
            # account and username/password are mutually exclusive
            'list --account=anything --username=foo --password=bar',
            'foo', 'bar'
            )

    def test_config_file_does_not_exist(self):
        self.assertRaises(
            main.LoginConfigError,
            self._test,
            'list --config /tmp/idontexist',
            '', '' # doesn't matter
            )
