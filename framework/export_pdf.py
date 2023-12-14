import inspect
import logging

from PyQt5.QtWidgets import QTableWidget
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from framework.logging_handler import PythagoraZenLogger

pythagorazen_logger = PythagoraZenLogger()
pythagorazen_logger.configure_logging()


class PDFExporter:
    def export(table: QTableWidget, file_path):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Get the logical (actual) order of columns
        logical_order = [
            table.horizontalHeader().logicalIndex(column)
            for column in range(table.columnCount())
        ]

        # Extract headers and data from QTableWidget based on the logical order
        headers = [table.horizontalHeaderItem(i).text() for i in logical_order]
        data = [headers]
        for row in range(table.rowCount()):
            row_data = [table.item(row, i).text() for i in logical_order]
            data.append(row_data)

        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0, colors.white),
            ]
        )

        # Create table and apply style
        pdf_table = Table(data)
        pdf_table.setStyle(table_style)

        # Build PDF document
        doc.build([pdf_table])
