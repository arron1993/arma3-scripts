import argparse
import os
from pathlib import Path

import uvicorn

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

    sub.add_parser("init", help="Create config.ini with defaults and placeholders to fill in")
    sub.add_parser("setup", help="Install steamcmd and the server, and log in to Steam (safe to re-run)")
    sub.add_parser("login", help="Log in to Steam interactively and cache the credentials")
    sub.add_parser("update", help="Update the server on the configured branch")

    mods_parser = sub.add_parser("mods", help="Manage workshop mods")
    mods_sub = mods_parser.add_subparsers(dest="mods_command", required=True)
    install_parser = mods_sub.add_parser("install", help="Download the configured mod list and lowercase them")
    install_parser.add_argument("--only", metavar="MOD_ID", help="Only install this mod from the mod list")

    use_parser = sub.add_parser("use", help="Switch to another mod list and install its mods")
    use_parser.add_argument("mod_list", help="Name of a mod list in mod_lists/, without .html")

    sub.add_parser("start", help="Start the server and headless clients; Ctrl+C stops them all")

    web_parser = sub.add_parser("web", help="Run the web interface")
    web_parser.add_argument("--host", default="127.0.0.1", help="Address to listen on")
    web_parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    web_parser.add_argument("--dev", action="store_true", help="Reload when the code changes")

    args = parser.parse_args()
    if args.command == "init":
        config.create(args.config, sorted(p.stem for p in mods.MOD_LISTS_DIR.glob("*.html")))
        print(f"Created {args.config}. Fill in the {config.PLACEHOLDER} values before running anything else.")
        return

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
        elif args.command == "use":
            mods.use(args.config, args.mod_list)
        elif args.command == "start":
            server.start(cfg)
        elif args.command == "web":
            os.environ["ARMA3_CONFIG"] = str(args.config.resolve())
            uvicorn.run("arma3.web:app", host=args.host, port=args.port, reload=args.dev, timeout_graceful_shutdown=1)
    except (steamcmd.SteamCmdError, mods.ModError, server.ServerError) as e:
        raise SystemExit(f"Error: {e}")


if __name__ == "__main__":
    main()
