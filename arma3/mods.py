import os
import re
from pathlib import Path

from . import config, steamcmd
from .config import Config

GAME_APPID = "107410"
MOD_LISTS_DIR = Path(__file__).resolve().parent.parent / "mod_lists"

MOD_ID = re.compile(r"https://.*?id=([0-9]+)")
DOWNLOADED = re.compile(r"Success\. Downloaded item (\d+)")


class ModError(Exception):
    pass


def load_mod_list(name: str) -> list[str]:
    path = MOD_LISTS_DIR / f"{name}.html"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in MOD_LISTS_DIR.glob("*.html"))) or "none"
        raise ModError(f"No mod list {path}. Available mod lists: {available}")

    mod_ids = list(dict.fromkeys(MOD_ID.findall(path.read_text(encoding="utf-8-sig"))))
    if not mod_ids:
        raise ModError(f"No workshop mods found in {path}")
    return mod_ids


def get_workshop_dir(cfg: Config, mod_id: str) -> Path:
    return cfg.install_dir / "steamapps/workshop/content" / GAME_APPID / mod_id


def download(cfg: Config, mod_ids: list[str]) -> list[str]:
    print(f"Downloading {len(mod_ids)} mod(s)...")
    commands = []
    for mod_id in mod_ids:
        commands += ["+workshop_download_item", GAME_APPID, mod_id, "validate"]

    downloaded = set(DOWNLOADED.findall(steamcmd.execute(cfg, *commands)))
    return [mod_id for mod_id in mod_ids if mod_id not in downloaded]


def lowercase(directory: Path):
    for root, dirnames, filenames in os.walk(directory, topdown=False):
        for name in filenames + dirnames:
            if name != name.lower():
                merge_into(Path(root, name), Path(root, name.lower()))


def merge_into(source: Path, dest: Path):
    if source.is_dir() and dest.is_dir():
        for child in source.iterdir():
            merge_into(child, dest / child.name)
        source.rmdir()
    else:
        source.replace(dest)


def install(cfg: Config, only=None):
    mod_ids = load_mod_list(cfg.mod_list)
    if only:
        if only not in mod_ids:
            raise ModError(f"Mod {only} is not in mod list {cfg.mod_list}")
        mod_ids = [only]

    failed = download(cfg, mod_ids)

    for mod_id in [m for m in mod_ids if m not in failed]:
        lowercase(get_workshop_dir(cfg, mod_id))

    if failed:
        raise ModError(f"Failed to download: {', '.join(failed)}")
    print(f"Installed {len(mod_ids)} mod(s)")


def use(config_path: Path, mod_list: str):
    load_mod_list(mod_list)
    config.set_mod_list(config_path, mod_list)
    cfg = config.load(config_path)
    print(f"Switched to {mod_list} (CDLC: {', '.join(cfg.cdlc) or 'none'})")
    install(cfg)
