import hmac
import hashlib
import secrets
import struct
import hashlib, hmac as _hmac
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

def generate_ecdh_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_key

def derive_shared_secret(private_key, peer_public_bytes):
    peer_public_key = serialization.load_pem_public_key(peer_public_bytes)
    return private_key.exchange(ec.ECDH(), peer_public_key)

def derive_key(master: bytes, purpose: str) -> bytes:
    prk = _hmac.new(b"vtp-v1-salt", master, hashlib.sha256).digest()
    return _hmac.new(prk, (purpose + "\x01").encode(), hashlib.sha256).digest()

TICKET_KEY   = derive_key(SERVER_SECRET, "ticket-issuance")
SESSION_KEY  = derive_key(SERVER_SECRET, "session-derivation")

def mac_data(key: bytes, seq: int, payload: str) -> str:
    """Unambiguous: 4-byte big-endian seq || utf-8 payload bytes."""
    seq_bytes = struct.pack(">I", seq)
    payload_bytes = payload.encode("utf-8")
    return hmac_sha256(key, seq_bytes + payload_bytes)

def hmac_sha256(key, msg: bytes):
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

def rand_hex(n_bytes):
    return secrets.token_hex(n_bytes)
