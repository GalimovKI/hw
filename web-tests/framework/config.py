from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = "http://www.uitestingplayground.com"
    browser: str = "chromium"
    headed: bool = False
    timeout_ms: int = 30_000
