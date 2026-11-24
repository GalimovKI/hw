"""Environment-only configuration; no dependency on application internals."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout: float

    @classmethod
    def from_env(cls):
        base_url = os.getenv("API_BASE_URL", "http://localhost:8080").rstrip("/")
        if urlparse(base_url).scheme not in {"http", "https"}:
            raise ValueError("API_BASE_URL must be an HTTP(S) URL")
        timeout = float(os.getenv("API_TIMEOUT", "10"))
        if timeout <= 0:
            raise ValueError("API_TIMEOUT must be positive")
        return cls(base_url, timeout)
