import re
import os
import stat
import argparse
import subprocess
import getpass
import tempfile
from pathlib import Path

ARMA3_APPID = "107410"
INSTALL_DIR = Path(f"/home/{getpass.getuser()}/arma3/gamedata")
MOD_DIR_TEMPLATE = "./steamapps/workshop/content/{}/{}"

# Get HC password from environment, fallback to a placeholder if not set
HC_PASSWORD = os.environ.get("HC_PASSWORD", "default_hc_password")

def write_script(name, script_content):
    scripts_dir = Path("./scripts")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = scripts_dir / f"{name}_start.sh"
    file_path.write_text(script_content)
    
    # Make the generated script executable
    file_path.chmod(file_path.stat().st_mode | stat.S_IEXEC)

def generate_start_script(modset_name, mods=None, cdlcs=None, profile_name=None, headless=False):
    script_base = ["cd ./gamedata && ./arma3server_x64 -nologs -enableHT -config=./config/server.cfg"]
    
    if profile_name:
        script_base.append(f'-name="{profile_name}"')

    # Combine CDLCs and workshop mods into a single list
    all_mods = []
    if cdlcs:
        all_mods.extend(cdlcs)
    if mods:
        all_mods.extend(mods)

    if all_mods:
        script_base.append(f'-mod="{";".join(all_mods)}"')

    if headless:
        for x in range(3):
            _script = script_base.copy()
            _modset_name = f"{modset_name}_hc{x}"
            _script.append(f"-client -connect=game.arron.id -password={HC_PASSWORD} -name={modset_name}_hc_{x}")
            write_script(_modset_name, ' '.join(_script))
    else:
        write_script(modset_name, ' '.join(script_base))

def download_mods_via_runscript(username, password, mod_ids):
    """Generates a temporary script file to run all SteamCMD commands in one session."""
    print(f"Preparing to download {len(mod_ids)} mods in a single SteamCMD session...")
    
    script_lines = [
        f"login {username} {password}",
        f"force_install_dir {INSTALL_DIR}"
    ]
    
    for mod_id in mod_ids:
        script_lines.append(f"workshop_download_item {ARMA3_APPID} {mod_id} validate")
    
    script_lines.append("quit")
    
    # Write to a secure temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_script:
        temp_script.write("\n".join(script_lines))
        temp_script_path = temp_script.name

    try:
        # Run SteamCMD using the secure temp script (hides password from process list)
        subprocess.run(["steamcmd", "+runscript", temp_script_path], check=True)
    finally:
        # Clean up the temporary file containing the password
        os.remove(temp_script_path)

def lowercase_bikey_files(base_dir: Path):
    """Recursively finds all .bikey files and renames them to lowercase."""
    print(f"Scanning for .bikey files in {base_dir} to lowercase...")
    
    count = 0
    # Iterate through all files recursively
    for file_path in base_dir.rglob("*"):
        try:
            # Catch permission errors when checking if it is a file
            if file_path.is_file() and file_path.suffix.lower() == ".bikey":
                lower_name = file_path.name.lower()
                
                # Only rename if the name actually needs changing
                if file_path.name != lower_name:
                    new_path = file_path.with_name(lower_name)
                    file_path.rename(new_path)
                    count += 1
        except PermissionError:
            # Skip any files or folders we don't have permission to read
            continue
            
    print(f"Successfully lowercased {count} .bikey files.")

def main(args):
    html_file = Path(args.filename)
    if not html_file.exists():
        print(f"Error: Could not find {args.filename}")
        return

    # Extract mod IDs using regex
    mods_html = html_file.read_text(encoding="utf-8")
    mod_ids = set(re.findall(r"https://.*?id=([0-9]+)", mods_html))
    
    if args.download_only:
        mod_ids = {args.download_only} & mod_ids

    mod_directories = [MOD_DIR_TEMPLATE.format(ARMA3_APPID, mod_id) for mod_id in mod_ids]

    # Handle downloading
    if args.download:
        mods_to_download = []
        for mod_id in mod_ids:
            if args.confirm:
                if input(f"Confirm download for {mod_id} (y/n): ").strip().lower() == 'y':
                    mods_to_download.append(mod_id)
            else:
                mods_to_download.append(mod_id)
        
        if mods_to_download:
            download_mods_via_runscript(args.username, args.password, mods_to_download)
        else:
            print("No mods selected for download.")

    lowercase_bikey_files(INSTALL_DIR)
    # Generate the startup scripts
    modset_name = html_file.stem
    profile = f"am_server_{modset_name}_profile"
    
    generate_start_script(modset_name=modset_name, mods=mod_directories, cdlcs=args.cdlc, profile_name=profile, headless=False)
    generate_start_script(modset_name=modset_name, mods=mod_directories, cdlcs=args.cdlc, headless=True)
    
    print(f"Successfully generated startup scripts in ./scripts/ for {modset_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arma 3 Server Mod Downloader and Script Generator")
    parser.add_argument("-u", "--username", dest="username", required=True, help="Steam username")
    parser.add_argument("-p", "--password", dest="password", required=True, help="Steam password")
    parser.add_argument("-f", "--file", dest="filename", required=True, help="Path to the Arma 3 launcher HTML preset file")
    parser.add_argument("--cdlc", nargs='+', help="List of CDLC folder names to load (e.g. vn gm ws csla spe)")

    # Converted global variables to CLI arguments
    parser.add_argument("--download", action="store_true", help="Execute the SteamCMD mod downloads")
    parser.add_argument("--confirm", action="store_true", help="Prompt for confirmation before downloading each mod")
    parser.add_argument("--download-only", dest="download_only", help="Provide a specific Mod ID to download only that mod")
    
    args = parser.parse_args()
    main(args)