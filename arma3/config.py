from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.ini"


@dataclass(frozen=True)
class Config:
    install_dir: Path
    branch: str | None
    steam_user: str
    server_config: str
    mod_list: str
    cdlc: list[str]
    hc_count: int
    hc_connect: str


def load(path: Path = DEFAULT_CONFIG) -> Config:
    if not path.exists():
        raise SystemExit(f"Config file not found: {path}")

    parser = configparser.ConfigParser()
    parser.read(path)

    try:
        return Config(
            install_dir=Path(parser["server"]["install_dir"]).expanduser(),
            branch=parser["server"].get("branch") or None,
            steam_user=parser["steam"]["user"],
            server_config=parser["server"]["config"],
            mod_list=parser["mods"]["list"],
            cdlc=parser["mods"].get("cdlc", "").split(),
            hc_count=parser.getint("headless", "count", fallback=0),
            hc_connect=parser.get("headless", "connect", fallback="127.0.0.1"),
        )
    except KeyError as e:
        raise SystemExit(f"Missing setting {e} in {path}")
