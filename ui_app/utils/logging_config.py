import logging
from config import LOG_DIR
def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_DIR / "sdlh.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
