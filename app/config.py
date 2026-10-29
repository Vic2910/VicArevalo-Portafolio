"""Public reads accept only unprivileged credentials; never log configuration."""
import base64
import json
import math
from dataclasses import dataclass
from urllib.parse import urlsplit

@dataclass(frozen=True, repr=False)
class PublicConfig:
    url: str | None
    key: str | None
    timeout: float = 6

    @classmethod
    def from_mapping(cls, values):
        try:
            timeout=float(values.get("PUBLIC_READ_TIMEOUT_SECONDS",6))
            if not math.isfinite(timeout) or timeout<=0: raise ValueError
        except (TypeError,ValueError):
            timeout=6
        return cls(values.get("SUPABASE_URL"),values.get("SUPABASE_PUBLISHABLE_KEY"),timeout)

    @property
    def valid(self):
        try:
            url=urlsplit(self.url or "")
            if url.username or url.password or url.query or url.fragment or url.path not in ("","/"): return False
            if not url.hostname or not (url.scheme=="https" or (url.scheme=="http" and url.hostname in ("localhost","127.0.0.1"))): return False
            if not isinstance(self.key,str) or any(c.isspace() for c in self.key): return False
            if self.key.startswith("sb_publishable_"): return len(self.key)>15
            payload=self.key.split(".")[1]
            claims=json.loads(base64.urlsafe_b64decode(payload+"="*(-len(payload)%4)))
            return claims.get("role")=="anon"
        except (ValueError,IndexError,TypeError):
            return False
