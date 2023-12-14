import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from framework.logging_handler import PythagoraZenLogger


class SignalTestFile1(QObject):
    """ """

    emit_method_1 = pyqtSignal(str)

    def __init__(self, main_app, signal_manager):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        self.main_app = main_app
        self.signal_manager = signal_manager
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug("Connecting instance...")

    def signal_test_file_1_emit_method_1(self):
        """ """

        self.emit_method_1.emit(
            "This is an emission from signal_test_file_1_emit_method"
        )

    def slot_in_signal_test_file_1(self, data):
        """

        :param data:

        """
        logging.debug(f"Emitted signal received in signal_test_file_1: {data}")
