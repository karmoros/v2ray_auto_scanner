import base64
import json
from urllib.parse import urlparse

def parse_vmess(url: str):
    # vmess://BASE64(JSON)
    try:
        raw = url.split("://", 1)[1]
        padded = raw + "=" * (-len(raw) % 4)
        decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
        data = json.loads(decoded)
        host = data.get("add")
        port = int(data.get("port", 443))
        return {"protocol": "vmess", "host": host, "port": port}
    except Exception:
        return None

def parse_vless(url: str):
    # vless://uuid@host:port?...
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 443
        params = dict(
            p.split("=") if "=" in p else (p, "")
            for p in parsed.query.split("&") if p
        )
        # type в URL это transport layer (tcp, ws, grpc)
        network = params.get("network") or params.get("type", "tcp")
        return {
            "protocol": "vless",
            "host": host,
            "port": int(port),
            "flow": params.get("flow", ""),
            "network": network,
            "sni": params.get("sni", ""),
            "security": params.get("security", ""),
            "fp": params.get("fp", ""),
            "sid": params.get("sid", ""),
            "path": params.get("path", ""),
        }
    except Exception:
        return None

def parse_ss(url: str):
    # ss://BASE64(method:password@host:port)#tag  или ss://method:password@host:port
    import base64
    try:
        raw = url.split("://", 1)[1]
        if "@" not in raw:
            base64_part = raw.split("#", 1)[0]
            padded = base64_part + "=" * (-len(base64_part) % 4)
            decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
            raw = decoded
        creds, addr = raw.rsplit("@", 1)
        host, port_str = addr.split(":", 1)
        return {"protocol": "ss", "host": host, "port": int(port_str)}
    except Exception:
        return None

def parse_generic(url: str, fallback_port: int = 443):
    # trojan://, tuic:// и т.п.
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or fallback_port
        if not host:
            return None
        proto = parsed.scheme
        return {"protocol": proto, "host": host, "port": int(port)}
    except Exception:
        return None

def parse_config_line(line: str, fallback_port: int = 443):
    if line.startswith("vmess://"):
        return parse_vmess(line)
    if line.startswith("vless://"):
        return parse_vless(line)
    if line.startswith("ss://"):
        return parse_ss(line)
    if "://" in line:
        return parse_generic(line, fallback_port)
    return None
