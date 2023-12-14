import logging

from PyQt5.QtCore import QObject, pyqtSignal

from framework.logging_handler import PythagoraZenLogger


class SignalTestFile2(QObject):
    """ """

    emit_method_2 = pyqtSignal(str)

    def __init__(self, main_app, signal_manager):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()

        self.main_app = main_app
        self.signal_manager = signal_manager
        logging.debug("Connecting instance...")

    def signal_test_file_2_emit_method_2(self):
        """ """
        self.emit_method_2.emit(
            "This is an emission from signal_test_file_2_emit_method"
        )

    def slot_in_signal_test_file_2(self, data):
        """

        :param data:

        """
        logging.debug(f"Emitted signal received in signal_test_file_2: {data}")
