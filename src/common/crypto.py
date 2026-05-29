import hmac
import hashlib
import secrets
import struct

def mac_data(key: bytes, seq: int, payload: str) -> str:
    """Unambiguous: 4-byte big-endian seq || utf-8 payload bytes."""
    seq_bytes = struct.pack(">I", seq)
    payload_bytes = payload.encode("utf-8")
    return hmac_sha256(key, seq_bytes + payload_bytes)

def hmac_sha256(key, msg: bytes):
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def rand_hex(n_bytes):
    return secrets.token_hex(n_bytes)
