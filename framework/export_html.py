import inspect
import logging

from PyQt5.QtWidgets import QTableWidget

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()


class HTMLExporter:
    def export(table: QTableWidget, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Set the spacing between columns
        column_spacing = 1

        # Get the logical (actual) order of columns
        logical_order = [
            table.horizontalHeader().logicalIndex(column)
            for column in range(table.columnCount())
        ]

        # Create the HTML content
        html_content = f"<html><body><table style='width: 100%; border-spacing: {column_spacing}px;'>"

        # Add table headers with bold and centered style
        html_content += "<tr>"
        for column in logical_order:
            item = table.horizontalHeaderItem(column)
            if item:
                html_content += f"<th style='text-align: center; font-weight: bold;'>{item.text()}</th>"
        html_content += "</tr>"

        # Add table rows
        for row in range(table.rowCount()):
            html_content += "<tr>"
            for column in logical_order:
                item = table.item(row, column)
                if item:
                    html_content += f"<td style='text-align: left;'>{item.text()}</td>"
            html_content += "</tr>"

        html_content += "</table></body></html>"

        # Write HTML content to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
