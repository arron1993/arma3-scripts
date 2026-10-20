from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.ini"
PLACEHOLDER = "CHANGE_ME"


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
        raise SystemExit(f"Config file not found: {path}. Run `python3 -m arma3 init` to create one.")

    parser = configparser.ConfigParser()
    parser.read(path)

    unset = [f"[{section}] {key}" for section in parser.sections() for key, value in parser[section].items() if value == PLACEHOLDER]
    if unset:
        raise SystemExit(f"Set these in {path}: {', '.join(unset)}")

    try:
        mod_list = parser["mods"]["list"]
        return Config(
            install_dir=Path(parser["server"]["install_dir"]).expanduser(),
            branch=parser["server"].get("branch") or None,
            steam_user=parser["steam"]["user"],
            server_config=parser["server"]["config"],
            mod_list=mod_list,
            cdlc=parser.get(mod_list, "cdlc", fallback="").split(),
            hc_count=parser.getint("headless", "count", fallback=0),
            hc_connect=parser.get("headless", "connect", fallback="127.0.0.1"),
        )
    except KeyError as e:
        raise SystemExit(f"Missing setting {e} in {path}")


def set_mod_list(path: Path, mod_list: str):
    parser = configparser.ConfigParser()
    parser.read(path)
    parser["mods"]["list"] = mod_list
    with open(path, "w") as f:
        parser.write(f)


def create(path: Path, mod_lists: list[str]):
    if path.exists():
        raise SystemExit(f"{path} already exists")

    parser = configparser.ConfigParser()
    parser["server"] = {"install_dir": "~/arma3/gamedata", "branch": "creatordlc", "config": "config/server.cfg"}
    parser["steam"] = {"user": PLACEHOLDER}
    parser["mods"] = {"list": PLACEHOLDER}
    parser["headless"] = {"count": "0", "connect": "127.0.0.1"}
    for mod_list in mod_lists:
        parser[mod_list] = {"cdlc": ""}

    with open(path, "w") as f:
        parser.write(f)
