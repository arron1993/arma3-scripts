import re
import argparse
import subprocess

ARMA3_APPID = 107410

INSTALL_DIR = "/home/arron/arma3/gamedata"
MOD_DIR_TEMPLATE = "./steamapps/workshop/content/{}/{}"


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
    print(";".join(mod_directories))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="username", required=True)
    parser.add_argument("-p", dest="password", required=True)
    parser.add_argument("-f", dest="filename", required=True)
    args = parser.parse_args()
    main(args)
