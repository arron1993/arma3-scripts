import functools
import re
import shutil
import subprocess

from .config import Config

SERVER_APPID = "233780"

NOT_INSTALLED = "steamcmd not found on PATH. Run `python3 -m arma3 setup` first."

LOGIN_FAILED = re.compile(r"Logging in user .*?(FAILED|ERROR)|Cached credentials not found")


class SteamCmdError(Exception):
    pass


def install():
    if is_installed():
        print("steamcmd already installed.")
        return

    def sudo(*args: str, **kwargs):
        subprocess.run(["sudo", *args], check=True, **kwargs)

    print("Installing steamcmd (needs sudo)...")
    sudo("apt", "install", "-y", "software-properties-common")
    sudo("add-apt-repository", "-y", "multiverse")
    sudo("dpkg", "--add-architecture", "i386")
    sudo("apt", "update")
    sudo(
        "debconf-set-selections",
        input='steam steam/question select I AGREE\nsteam steam/license note \n',
        text=True,
    )
    sudo("apt", "install", "-y", "lib32gcc-s1", "steamcmd")


def is_installed() -> bool:
    return shutil.which("steamcmd") is not None


def requires_steamcmd(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_installed():
            raise SystemExit(NOT_INSTALLED)
        return func(*args, **kwargs)
    return wrapper


@requires_steamcmd
def prompt_login(cfg: Config):
    subprocess.run(["steamcmd", "+login", cfg.steam_user, "+quit"], check=True)


@requires_steamcmd
def execute(cfg: Config, *commands: str) -> str:
    args = ["steamcmd", "+force_install_dir", str(cfg.install_dir), "+login", cfg.steam_user]
    args += commands
    args.append("+quit")

    proc = subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = []
    for line in proc.stdout:
        print(line, end="")
        output.append(line)
    proc.wait()

    text = "".join(output)
    if LOGIN_FAILED.search(text):
        raise SteamCmdError("Steam login failed. Run `python3 -m arma3 login` to refresh cached credentials.")
    return text


def update_server(cfg: Config):
    cmd = ["+app_update", SERVER_APPID]
    if cfg.branch:
        cmd += ["-beta", cfg.branch]
    cmd.append("validate")

    output = execute(cfg, *cmd)
    if f"Success! App '{SERVER_APPID}' fully installed" not in output:
        raise SteamCmdError("Server install/update did not report success; see SteamCMD output above.")
