"""RFC 8032 vector verifies the template seed uses Relay's Ed25519 wire format."""
import base64
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'common'))
from relay_identity import identity


class RelayIdentityTests(unittest.TestCase):
    def test_rfc8032_seed_and_public_key(self):
        seed = '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60'
        value = identity(seed)
        decode = lambda s: base64.urlsafe_b64decode(s + '=')
        self.assertEqual(decode(value['secret_key']).hex(), seed)
        self.assertEqual(decode(value['public_key']).hex(),
                         'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
        self.assertRegex(value['id'], r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$')
        self.assertEqual(value, identity(seed))
        self.assertNotEqual(value['id'], identity('00' * 32)['id'])

    def test_invalid_seed_rejected(self):
        for seed in ['', 'a' * 63, 'z' * 64, '00' * 64]:
            with self.assertRaises(ValueError):
                identity(seed)
