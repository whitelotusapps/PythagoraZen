import inspect
import logging

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from framework.logging_handler import PythagoraZenLogger


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Define the formats for different JSON elements
        self.json_formats = {
            "string": QTextCharFormat(),
            "number": QTextCharFormat(),
            "boolean": QTextCharFormat(),
            "null": QTextCharFormat(),
            "key": QTextCharFormat(),
            "timestamp": QTextCharFormat(),  # New format for timestamps
        }

        # Set the colors and styles for each format
        self.json_formats["string"].setForeground(QColor(0, 128, 0))  # Dark green
        self.json_formats["number"].setForeground(QColor(0, 0, 255))  # Blue
        self.json_formats["boolean"].setForeground(
            QColor(184, 134, 11)
        )  # Dark goldenrod
        self.json_formats["null"].setForeground(QColor(139, 0, 139))  # Dark magenta
        self.json_formats["key"].setForeground(QColor(139, 0, 0))  # Dark red
        self.json_formats["key"].setFontWeight(QFont.Bold)
        self.json_formats["timestamp"].setForeground(
            QColor(255, 165, 0)
        )  # Orange for timestamps

        # Define the regular expressions for each JSON element
        self.rules = []
        self.rules += [
            (
                QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),
                0,
                self.json_formats["string"],
            )
        ]
        self.rules += [
            (QRegularExpression(r"-?\b\d+(\.\d+)?\b"), 0, self.json_formats["number"])
        ]
        self.rules += [
            (QRegularExpression(r"\b(?:true|false)\b"), 0, self.json_formats["boolean"])
        ]
        self.rules += [(QRegularExpression(r"\bnull\b"), 0, self.json_formats["null"])]
        self.rules += [
            (
                QRegularExpression(r'"([^"\\]*(\\.[^"\\]*)*)"(\s*:\s*)'),
                1,
                self.json_formats["key"],
            )
        ]
        self.rules += [
            (
                QRegularExpression(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b"),
                0,
                self.json_formats["timestamp"],
            )
        ]

    def highlightBlock(self, text):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        for expression, nth, format in self.rules:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(nth), match.capturedLength(nth), format
                )
