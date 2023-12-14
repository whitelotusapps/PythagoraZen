# export_manager.py
import inspect
import logging

from PyQt5.QtWidgets import QFileDialog

from framework.logging_handler import PythagoraZenLogger

from framework.export_csv import CSVExporter
from framework.export_html import HTMLExporter
from framework.export_pdf import PDFExporter
from framework.export_xlsx import XLSXExporter


class ExportManager:
    def __init__(self, table):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.table = table

    def set_buttons(self, html_button, pdf_button, csv_button, xlsx_button):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.html_export_button = html_button
        self.pdf_export_button = pdf_button
        self.csv_export_button = csv_button
        self.xlsx_export_button = xlsx_button

    def export_to_html(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        file_path, filter = QFileDialog.getSaveFileName(
            self.html_export_button, "Save HTML File", "", "HTML Files (*.html)"
        )
        if file_path:
            HTMLExporter.export(self.table, file_path)

    def export_to_pdf(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        file_path, filter = QFileDialog.getSaveFileName(
            self.pdf_export_button, "Save PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            PDFExporter.export(self.table, file_path)

    def export_to_csv(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        file_path, filter = QFileDialog.getSaveFileName(
            self.csv_export_button, "Save CSV File", "", "CSV Files (*.csv)"
        )
        if file_path:
            CSVExporter.export(self.table, file_path)

    def export_to_xlsx(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        file_path, filter = QFileDialog.getSaveFileName(
            self.xlsx_export_button, "Save XLSX File", "", "XLSX Files (*.xlsx)"
        )
        if file_path:
            XLSXExporter.export(self.table, file_path)

    def hide_save_buttons(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.html_export_button.hide()
        self.pdf_export_button.hide()
        self.csv_export_button.hide()
        self.xlsx_export_button.hide()

    def show_save_buttons(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.html_export_button.show()
        self.pdf_export_button.show()
        self.csv_export_button.show()
        self.xlsx_export_button.show()
