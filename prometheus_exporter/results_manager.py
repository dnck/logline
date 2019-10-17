# -*- coding: utf-8 -*-
"""
This module is a simple manager for the standard Python logging module. It's
primary contribution is its ability to create a default var/log directory
for storing the log file when constructed with Arg output='file'

Usage:
    from log_manager import LogManager


    file_logger = LogManager(level="debug", output="file") # logs to file
    stdout_logger = LogManager(level="debug", output="stdout") # logs to stdout

    file_logger.log.info("Hello world!")

"""
import logging
import os
import sys

LEVELS = {"notset": logging.NOTSET, "debug": logging.DEBUG,
          "info": logging.INFO, "warning": logging.WARNING,
          "error": logging.ERROR, "critical": logging.CRITICAL
          }

class LogManager:
    """
    A simple class for managing logging for the application.
    """

    PY_DIRNAME, PY_FILENAME = os.path.split(os.path.abspath(__file__))

    def __init__(self, level="debug", output="stdout",
                 filename="pendulum_export.log"
                ):
        """
        Args:
            level (str): All of the default log levels from the
                logging module are supported.
            output (str): Either 'stdout' or 'file'. If 'file', then messages
                are directed to the var/log/py_exchange_rates.log file.
        """
        self.log = logging
        self.level = LEVELS[level]

        if output == "file":
            self._root_dir = os.path.dirname(self.PY_DIRNAME)
            self._var_dir = os.path.join(self._root_dir, "var")
            mkdir_if_not_exists(self._var_dir)

            self._log_dir = os.path.join(self._var_dir, "log")
            mkdir_if_not_exists(self._log_dir)

            self._log_file_name = os.path.join(
                ".", self._log_dir, filename
            )
            self.configure_logger(self._log_file_name)
        else:
            self.configure_logger()

    def configure_logger(self, filename=None):
        """A docstring"""
        if filename:
            self.log.basicConfig(
                filename=self._log_file_name,
                level=self.level,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )
        else:
            self.log.basicConfig(
                stream=sys.stdout,
                level=self.level,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )

    def info(self, msg):
        """Emits a msg at the info level."""
        self.log.info(msg)

    def debug(self, msg):
        """Emits a msg at the debug level."""
        self.log.debug(msg)

    def warning(self, msg):
        """Emits a msg at the warning level."""
        self.log.warning(msg)

    def error(self, msg):
        """Emits a msg at the error level."""
        self.log.error(msg)

    def critical(self, msg):
        """Emits a msg at the critical level."""
        self.log.critical(msg)

    def exception(self, msg):
        """Emits a msg and the error trace which caused the exception."""
        self.log.exception(msg)

def mkdir_if_not_exists(dirname):
    """Make a directory if it does not exist."""
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
