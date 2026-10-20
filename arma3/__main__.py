import argparse
from pathlib import Path

from . import config, mods, server, steamcmd
from .config import Config

PROFILE_DIRS = [
    Path.home() / ".local/share/Arma 3",
    Path.home() / ".local/share/Arma 3 - Other Profiles",
]


def setup(cfg: Config):
    steamcmd.install()

    cfg.install_dir.mkdir(parents=True, exist_ok=True)
    for d in PROFILE_DIRS:
        d.mkdir(parents=True, exist_ok=True)

    print(f"Logging in to Steam as {cfg.steam_user} (enter password / Steam Guard code if asked)...")
    steamcmd.prompt_login(cfg)

    print(f"Installing server into {cfg.install_dir}...")
    steamcmd.update_server(cfg)


def main():
    parser = argparse.ArgumentParser(prog="arma3", description="Arma 3 dedicated server management")
    parser.add_argument("-c", "--config", type=Path, default=config.DEFAULT_CONFIG, help="Path to config.ini")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Install steamcmd and the server, and log in to Steam (safe to re-run)")
    sub.add_parser("login", help="Log in to Steam interactively and cache the credentials")
    sub.add_parser("update", help="Update the server on the configured branch")

    mods_parser = sub.add_parser("mods", help="Manage workshop mods")
    mods_sub = mods_parser.add_subparsers(dest="mods_command", required=True)
    install_parser = mods_sub.add_parser("install", help="Download the configured mod list and lowercase them")
    install_parser.add_argument("--only", metavar="MOD_ID", help="Only install this mod from the mod list")

    sub.add_parser("start", help="Start the server and headless clients; Ctrl+C stops them all")

    args = parser.parse_args()
    cfg = config.load(args.config)

    try:
        if args.command == "setup":
            setup(cfg)
        elif args.command == "login":
            steamcmd.prompt_login(cfg)
        elif args.command == "update":
            steamcmd.update_server(cfg)
        elif args.command == "mods" and args.mods_command == "install":
            mods.install(cfg, args.only)
        elif args.command == "start":
            server.start(cfg)
    except (steamcmd.SteamCmdError, mods.ModError, server.ServerError) as e:
        raise SystemExit(f"Error: {e}")


if __name__ == "__main__":
    main()
