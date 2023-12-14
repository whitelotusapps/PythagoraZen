import csv
import logging

from PyQt5.QtWidgets import QTableWidget

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()


class CSVExporter:
    def export(table: QTableWidget, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        with open(file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)

            # Get the logical (actual) order of columns
            logical_order = [
                table.horizontalHeader().logicalIndex(column)
                for column in range(table.columnCount())
            ]

            # Write column headers based on the logical order
            headers = [table.horizontalHeaderItem(i).text() for i in logical_order]
            writer.writerow(headers)

            # Write data rows
            for row in range(table.rowCount()):
                # Manually rearrange the data based on the logical order
                row_data = [table.item(row, i).text() for i in logical_order]

                # Write the rearranged row data
                writer.writerow(row_data)
