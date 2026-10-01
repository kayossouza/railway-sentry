"""Derive Relay's documented key format from a Railway-generated 32-byte seed."""
import base64
import re
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def identity(seed):
    if not re.fullmatch(r'[0-9a-f]{64}', seed):
        raise ValueError('RELAY_KEY_SEED must be 64 lowercase hexadecimal characters')
    secret = bytes.fromhex(seed)
    public = Ed25519PrivateKey.from_private_bytes(secret).public_key().public_bytes_raw()
    encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip('=')
    return {'secret_key': encode(secret), 'public_key': encode(public),
            'id': str(uuid.uuid5(uuid.NAMESPACE_OID, encode(public)))}
