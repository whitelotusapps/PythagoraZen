import inspect
import logging

from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget

from framework.logging_handler import PythagoraZenLogger


class StatusWindow(QWidget):
    def __init__(self, endpoint):
        super().__init__()
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.init_ui()
        self.setWindowTitle(f"Status Window - {endpoint}")

    def init_ui(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # self.setWindowTitle('Status Window')
        self.setGeometry(400, 400, 1400, 400)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

    def update_status(self, message):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.text_edit.append(message)
        QApplication.processEvents()
