import inspect
import logging

import xlsxwriter
from PyQt5.QtWidgets import QTableWidget

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()


class XLSXExporter:
    def export(table: QTableWidget, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()

        # Get the logical (actual) order of columns
        logical_order = [
            table.horizontalHeader().logicalIndex(column)
            for column in range(table.columnCount())
        ]

        # Define a bold format for headers
        bold_format = workbook.add_format(
            {"bold": True, "align": "center", "valign": "vcenter"}
        )

        # Write headers to the first row with the bold format
        headers = [table.horizontalHeaderItem(i).text() for i in logical_order]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, bold_format)

        # Write data starting from the second row
        for row in range(table.rowCount()):
            for col_num, header in enumerate(headers):
                item = table.item(row, logical_order[col_num])
                if item:
                    worksheet.write(row + 1, col_num, item.text())

        # Set the width of columns based on the maximum length of the data in each column
        for col_num, header in enumerate(headers):
            max_length = max(
                [
                    len(str(table.item(row, logical_order[col_num]).text()))
                    for row in range(table.rowCount())
                ]
            )
            worksheet.set_column(
                col_num, col_num, max_length * 1.2
            )  # Adjust the multiplier factor

        workbook.close()
