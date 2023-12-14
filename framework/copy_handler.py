import inspect
import logging

from PyQt5.QtWidgets import QAction, QApplication, QMenu

from framework.logging_handler import PythagoraZenLogger
pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()



class CopyHandler:
    @staticmethod
    def create_copy_menu(table, pos):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        menu = QMenu()

        copy_action = QAction("Copy", table)
        copy_action.triggered.connect(lambda: CopyHandler.copy_selection(table))
        menu.addAction(copy_action)

        menu.exec_(table.viewport().mapToGlobal(pos))

    @staticmethod
    def copy_selection(table):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        selection = table.selectedRanges()
        if selection:
            rows = set()
            columns = set()

            for selected_range in selection:
                rows.update(
                    range(selected_range.topRow(), selected_range.bottomRow() + 1)
                )
                columns.update(
                    range(selected_range.leftColumn(), selected_range.rightColumn() + 1)
                )

            data = []

            # Use logical index to get the correct order of column headers
            header_order = [
                table.horizontalHeaderItem(
                    table.horizontalHeader().logicalIndex(column)
                ).text()
                for column in columns
            ]

            # Include column headers as the first row
            data.append(header_order)

            for row in rows:
                row_data = [
                    table.item(
                        row,
                        table.horizontalHeader().logicalIndex(
                            header_order.index(header)
                        ),
                    ).text()
                    for header in header_order
                ]
                data.append(row_data)

            clipboard = QApplication.clipboard()
            clipboard.setText(CopyHandler.format_data(data))

    @staticmethod
    def format_data(data):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return "\n".join(["\t".join(row) for row in data])
