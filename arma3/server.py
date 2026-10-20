import os
import subprocess

from . import mods
from .config import Config

EXECUTABLE = "./arma3server_x64"
PROFILE = "am_server_a3_aegis_profile"


class ServerError(Exception):
    pass


def get_mod_arg(cfg: Config) -> str:
    mod_ids = mods.load_mod_list(cfg.mod_list)
    missing = [mod_id for mod_id in mod_ids if not mods.get_workshop_dir(cfg, mod_id).exists()]
    if missing:
        raise ServerError(f"Mods not installed: {', '.join(missing)}. Run `python3 -m arma3 mods install`.")

    paths = [str(mods.get_workshop_dir(cfg, mod_id).relative_to(cfg.install_dir)) for mod_id in mod_ids]
    return "-mod=" + ";".join(cfg.cdlc + paths)


def get_server_args(cfg: Config, mod_arg: str) -> list[str]:
    return [
        EXECUTABLE,
        "-enableHT",
        f"-config={cfg.server_config}",
        f"-name={PROFILE}",
        mod_arg,
    ]


def get_hc_args(cfg: Config, mod_arg: str, number: int, password: str) -> list[str]:
    return [
        EXECUTABLE,
        "-enableHT",
        "-client",
        f"-connect={cfg.hc_connect}",
        f"-password={password}",
        f"-name=hc_{number}",
        mod_arg,
    ]


def start(cfg: Config):
    if not (cfg.install_dir / EXECUTABLE).exists():
        raise ServerError(f"No server in {cfg.install_dir}. Run `python3 -m arma3 setup`.")

    password = os.environ.get("HC_PASSWORD")
    if cfg.hc_count and not password:
        raise ServerError("HC_PASSWORD is not set. Set it to the server password, or set [headless] count = 0.")

    mod_arg = get_mod_arg(cfg)
    logs_dir = cfg.install_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    print(f"Starting server with mod list {cfg.mod_list}...")
    processes = [subprocess.Popen(get_server_args(cfg, mod_arg), cwd=cfg.install_dir)]
    server = processes[0]

    for number in range(cfg.hc_count):
        log_path = logs_dir / f"hc_{number}.log"
        print(f"Starting headless client {number}, logging to {log_path}")
        with open(log_path, "w") as log:
            processes.append(subprocess.Popen(
                get_hc_args(cfg, mod_arg, number, password),
                cwd=cfg.install_dir,
                stdout=log,
                stderr=subprocess.STDOUT,
            ))

    try:
        server.wait()
        print(f"Server exited with code {server.returncode}")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            process.wait()
