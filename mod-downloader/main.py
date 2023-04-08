import re
import os
import stat
import argparse
import subprocess
import getpass

from pathlib import Path

ARMA3_APPID = 107410

INSTALL_DIR = f"/home/arron/{getpass.getuser()}/gamedata"
MOD_DIR_TEMPLATE = "./steamapps/workshop/content/{}/{}"

HC_PASSWORD = os.environ.get("HC_PASSWORD")


def write_script(name, script):
    if not os.path.exists("./scripts"):
        os.makedirs("./scripts")
    file_ = f"./scripts/{name}_start.sh"

    with open(file_, 'w') as f:
        f.write(script)

    st = os.stat(file_)
    os.chmod(file_, st.st_mode | stat.S_IEXEC)


def generate_start_script(modset_name=None, mods=None, profile_name=None,  headless=False):
    """
    cd ./gamedata && ./arma3server_x64 -name="am_server_vanilla_1" -enableHT -config=./config/server.cfg -mod="./steamapps/workshop/content/107410/1858075458;./steamapps/workshop/content/107410/2158809703;./steamapps/workshop/content/107410/333310405;./steamapps/workshop/content/107410/2479270597;./steamapps/workshop/content/107410/450814997;./steamapps/workshop/content/107410/825179978;./steamapps/workshop/content/107410/1224892496;./steamapps/workshop/content/107410/1158566432;./steamapps/workshop/content/107410/861133494;./steamapps/workshop/content/107410/1858070328;./steamapps/workshop/content/107410/1862208264;./steamapps/workshop/content/107410/2912941775;./steamapps/workshop/content/107410/2261809404;./steamapps/workshop/content/107410/612930542;./steamapps/workshop/content/107410/1808238502"
    """
    script = ["cd ./gamedata && ./arma3server_x64 -nologs -enableHT -config=./config/server.cfg"]

    if mods:
        script.append(f'-mod="{";".join(mods)}"')

    if headless:
        for x in range(3):
            _script = script.copy()
            _modset_name = f"{modset_name}_hc{x}"
            _script.append(f"-client -connect=game.arron.id -password={HC_PASSWORD} -name={modset_name}")
            write_script(_modset_name, ' '.join(_script))
    else:
        write_script(modset_name, ' '.join(script))


def main(args):
    with open(args.filename) as mods_html_file:
        mods_html = mods_html_file.read()

    mod_ids = set(re.findall(r"https://.*?id=([0-9]+)", mods_html))
    mod_directories = []
    for mod_id in mod_ids:
        mod_directories.append(MOD_DIR_TEMPLATE.format(ARMA3_APPID, mod_id))
        subprocess.run(
            f"steamcmd +login {args.username} {args.password} +force_install_dir {INSTALL_DIR} +workshop_download_item {ARMA3_APPID} {mod_id} validate +quit".split()
        )

    modset_name = Path(args.filename).stem
    generate_start_script(modset_name=modset_name, mods=mod_directories, profile_name=f"am_server_{modset_name}_profile", headless=False)
    generate_start_script(modset_name=modset_name, mods=mod_directories, headless=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="username", required=True)
    parser.add_argument("-p", dest="password", required=True)
    parser.add_argument("-f", dest="filename", required=True)
    args = parser.parse_args()
    main(args)
