# ==========================================
# Arma 3 Linux Server Update Script
# ==========================================

# --- Configuration ---
# Update these paths to match your server's directory structure
STEAMCMD_PATH=$(which steamcmd)
ARMA3_DIR="$HOME/arma3/gamedata"
APP_ID="233780"
# ---------------------

echo "================================="
echo " Starting Arma 3 Server Update "
echo "================================="

# Check if SteamCMD exists
if [ -z "$STEAMCMD_PATH" ]; then    
    echo "Error: steamcmd.sh not found in $STEAMCMD_DIR."
    echo "Please verify the STEAMCMD_DIR path in this script."
    exit 1
fi

# Run SteamCMD to update and validate the Arma 3 server
"steamcmd" \
    +force_install_dir "$ARMA3_DIR" \
    +login anonymous \
    +app_update "$APP_ID" validate \
    +quit

echo "================================="
echo " Arma 3 Update Process Complete"
echo "=================================":
