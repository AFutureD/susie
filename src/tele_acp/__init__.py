import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from .constant import APP_NAME

log_dir = Path("./logs/")
log_dir.mkdir(parents=True, exist_ok=True)

log_hander = TimedRotatingFileHandler(log_dir / f"{APP_NAME}.log", when="midnight")
log_hander.setLevel(logging.INFO)

error_handler = RotatingFileHandler(log_dir / "error.log")
error_handler.setLevel(logging.ERROR)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), log_hander, error_handler],
)
