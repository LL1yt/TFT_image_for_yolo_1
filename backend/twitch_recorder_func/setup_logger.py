import logging
from logging.handlers import TimedRotatingFileHandler


class SetupLogger:
    def __init__(
        self,
    ):
        self.log_file = "logs/info.log"

    def setup_logger(self):
        log_formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_handler = TimedRotatingFileHandler(
            self.log_file, when="D", interval=1, backupCount=10
        )
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.INFO)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)
