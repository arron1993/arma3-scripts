INSTALL_DIR=/home/$(whoami)/arma3/gamedata
echo $INSTALL_DIR
mkdir -p $INSTALL_DIR

if ! $(which steamcmd); then
	sudo add-apt-repository multiverse
	sudo apt install software-properties-common
	sudo dpkg --add-architecture i386
	sudo apt update
	sudo apt install lib32gcc-s1 steamcmd rename 
fi

steamcmd +login arron_cli +force_install_dir $INSTALL_DIR app_update 233780 validate
mkdir -p ~/".local/share/Arma 3" && mkdir -p ~/".local/share/Arma 3 - Other Profiles"

