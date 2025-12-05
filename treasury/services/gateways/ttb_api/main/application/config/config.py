from typing import Any

import os
import logging
from dotenv import load_dotenv
from dotenv import dotenv_values
from pythonjsonlogger.json import JsonFormatter

from treasury.services.gateways.ttb_api.main.application.utils.datetime_utils import DateTimeUtils

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env'))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env.local'))
_config = {
    **dotenv_values(os.path.join(os.path.dirname(__file__), '.env')),  # load shared development variables
    **dotenv_values(os.path.join(os.path.dirname(__file__), '.env.secret')),  # load sensitive variables
    **dotenv_values(os.path.join(os.path.dirname(__file__), '.env.local')),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}

environment = os.environ.get('ENV', 'dev').lower()


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = DateTimeUtils.get_utc_now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


class GlobalConfig:
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    _logger_initialized = False

    my_handler = logging.StreamHandler()

    @classmethod
    def init_logger(cls) -> None:
        if cls._logger_initialized:
            return

        cls.my_handler.setLevel(logging.INFO)
        cls.my_handler.setFormatter(CustomFormatter())

        cls.my_handler.setLevel(cls.LOGLEVEL)
        logging.basicConfig(level=cls.LOGLEVEL, handlers=[cls.my_handler], force=True)
        _logger_initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:

        logging.getLogger().setLevel(cls.LOGLEVEL)
        logger = logging.getLogger(name)
        handlers = logger.handlers
        parent_handlers = logger.parent.handlers
        root_handlers = logger.root.handlers

        for handler in handlers:
            if handler != cls.my_handler:
                logger.removeHandler(handler)

        for handler in parent_handlers:
            if handler != cls.my_handler:
                logger.parent.removeHandler(handler)

        for handler in root_handlers:
            if handler != cls.my_handler:
                logger.root.removeHandler(handler)

        return logger


def __getattr__(name) -> Any | None:
    return os.environ.get(name, None)


GlobalConfig.init_logger()
