import logging

# sh = logging.StreamHandler()
# sh.setLevel(logging.DEBUG)

# fh = logging.FileHandler("tele-acp.log")
# fh.setLevel(logging.DEBUG)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("tele-acp.log")],
)
