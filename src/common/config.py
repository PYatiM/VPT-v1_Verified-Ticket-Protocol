import os

_raw = os.environ.get("VTP_SERVER_SECRET")
if not _raw:
    raise RuntimeError("VTP_SERVER_SECRET is not set"
                     "Generate one: python -c \"import secrets; print(secrets.token_hex(32))\""
                    )
SECRET_KEY = _raw.encode()
