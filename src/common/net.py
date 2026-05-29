from common.config import TRUSTED_PROXY

def get_client_ip(writer, headers: dict | None = None) -> str:
    peer_ip = writer.get_extra_info("peername")[0]
    if TRUSTED_PROXY and peer_ip == TRUSTED_PROXY and headers:
        forwarded = headers.get("x-forwarded-for", "")
        candidate = forwarded.split(",")[0].strip()
        if candidate:
            return candidate
    return peer_ip