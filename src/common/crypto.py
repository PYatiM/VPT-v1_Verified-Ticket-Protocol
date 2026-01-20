import hmac
import hashlib
import secrets

def hmac_sha256(key, msg: bytes):
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def rand_hex(n_bytes):
    return secrets.token_hex(n_bytes)
