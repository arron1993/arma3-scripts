import re
import argparse

ARMA3_APPID = 107410

INSTALL_DIR = "/home/arron/arma3/gamedata"

def main(args):
    with open("./sog_mods.html") as mods_html_file:
        mods_html = mods_html_file.read()

    mod_ids = set(re.findall(r'https://.*?id=([0-9]+)', mods_html))
    for mod_id in mod_ids:
        print(f"steamcmd +login {args.username} \"{args.password}\" +force_install_dir {INSTALL_DIR} +workshop_download_item {ARMA3_APPID} {mod_id} validate +quit")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="username", required=True)
    parser.add_argument("-p", dest="password", required=True)

    args = parser.parse_args()
    main(args)