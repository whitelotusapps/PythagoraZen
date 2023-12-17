import logging
import os
from datetime import datetime
import colorlog

class PythagoraZenLogger:
    _is_configured = False
    _logfile_path = None

    @classmethod
    def configure_logging(cls):
        if cls._is_configured:
            return  # Don't configure logging again if it's already done

        # Configure the logging with colorization
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(filename)s - %(lineno)d\t- %(levelname)-8s:\t%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                reset=True,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
                secondary_log_colors={},
                style="%",
            )
        )

        file_handler = logging.FileHandler(cls._logfile_path)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(lineno)d \t- %(levelname)-8s:\t%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[handler, file_handler],
        )

        cls._is_configured = True

    @classmethod
    def create_logfile(cls):
        if cls._logfile_path:
            return  # Logfile already created

        # Get the absolute path to the "LOGS" folder in the root of the project
        logs_folder = os.path.join(os.path.dirname(__file__), "../LOGS")

        # Ensure the "LOGS" folder exists, create it if not
        os.makedirs(logs_folder, exist_ok=True)

        # Get the current date and time in a specific format (e.g., YYYY-MM-DD_HH-MM-SS)
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Set up the file handler with the logfile in the "LOGS" folder
        logfile_name = f"{current_datetime}_logfile.log"
        cls._logfile_path = os.path.join(logs_folder, logfile_name)