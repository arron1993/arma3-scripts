# arma3-scripts

Run everything from the repo folder.

| Command | What it does |
|---|---|
| `python3 -m arma3 init` | Create `config.ini`. Fill in the `CHANGE_ME` values. |
| `python3 -m arma3 setup` | Install steamcmd and the server, and log in to Steam. |
| `python3 -m arma3 login` | Log in to Steam again if a command says the login failed. |
| `python3 -m arma3 update` | Update the server. |
| `python3 -m arma3 mods install` | Download and update the current mod list's mods. |
| `python3 -m arma3 mods install --only <id>` | Download one mod from the current mod list. |
| `python3 -m arma3 use <name>` | Switch to `mod_lists/<name>.html` and install its mods. |
| `HC_PASSWORD=<password> python3 -m arma3 start` | Start the server and headless clients. Ctrl+C stops them all. |

Mod lists are exported from the Arma 3 launcher and saved in `mod_lists/`.
CDLC for each mod list goes in its section in `config.ini`, e.g. `cdlc = ws`.

If running from scratch the server.cfg needs creating manually
