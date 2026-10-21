import asyncio
import contextlib
import os
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from . import config, mods, steamcmd

CONFIG_PATH = Path(os.environ.get("ARMA3_CONFIG", config.DEFAULT_CONFIG))

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


def get_update_log_path(cfg: config.Config) -> Path:
    return cfg.install_dir / "logs/update.log"


def run_update(cfg: config.Config):
    with open(get_update_log_path(cfg), "a", buffering=1) as log, contextlib.redirect_stdout(log):
        try:
            steamcmd.update_server(cfg)
        except (steamcmd.SteamCmdError, SystemExit) as e:
            print(f"Error: {e}")


async def follow(path: Path):
    while not path.exists():
        await asyncio.sleep(0.5)
    with open(path, errors="replace") as log:
        while True:
            line = log.readline()
            if line:
                yield f"data: {line.rstrip()}\n\n"
            else:
                await asyncio.sleep(0.5)


@app.get("/")
def index(request: Request):
    mod_lists = sorted(p.stem for p in mods.MOD_LISTS_DIR.glob("*.html"))
    return templates.TemplateResponse(request, "index.html", {"mod_lists": mod_lists})


@app.post("/api/update", status_code=202)
def update(background_tasks: BackgroundTasks):
    cfg = config.load(CONFIG_PATH)
    log_path = get_update_log_path(cfg)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("")
    background_tasks.add_task(run_update, cfg)


@app.get("/api/update/log")
def stream_update_log():
    log_path = get_update_log_path(config.load(CONFIG_PATH))
    return StreamingResponse(follow(log_path), media_type="text/event-stream")


@app.post("/api/mods/install")
def install_mods(only: Optional[str] = None):
    mods.install(config.load(CONFIG_PATH), only)


@app.post("/api/use/{mod_list}")
def use(mod_list: str):
    mods.use(CONFIG_PATH, mod_list)
