"""
SQLPhantom PySide6 Database Schema Tree & Table Dump Explorer screen.
"""

from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sqlphantom.domain.schema import ColumnSchema, DatabaseSchema, TableDump, TableSchema


class SchemaViewerScreen(QWidget):
    """
    Interactive database schema tree and virtualized table dump viewer.
    Allows penetration testers to browse extracted schemas, tables, and columns,
    and preview dumped data records with one-click CSV export.
    """

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._current_dump: TableDump | None = None
        self._schemas: list[DatabaseSchema] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header bar
        top_bar = QHBoxLayout()
        title_lbl = QLabel("Database Schema & Table Data Explorer")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #F8FAFC;")
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()

        self.btn_export_csv = QPushButton("Export Table to CSV")
        self.btn_export_csv.setProperty("class", "secondary")
        self.btn_export_csv.clicked.connect(self._export_csv)
        top_bar.addWidget(self.btn_export_csv)

        layout.addLayout(top_bar)

        self.lbl_status = QLabel("Select a table or column from the schema hierarchy.")
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        # Splitter: Left Schema Tree, Right Table Grid
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Schema Tree
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Extracted Database Architecture:"))

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Database Object", "Type / Rows"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.itemClicked.connect(self._on_tree_item_clicked)
        left_layout.addWidget(self.tree)
        splitter.addWidget(left_frame)

        # Right: Table Dump Grid
        right_frame = QFrame()
        right_frame.setProperty("class", "card-frame")
        right_layout = QVBoxLayout(right_frame)

        self.lbl_dump_title = QLabel("No table selected.")
        self.lbl_dump_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #A855F7;")
        right_layout.addWidget(self.lbl_dump_title)

        self.table_grid = QTableWidget()
        self.table_grid.setStyleSheet("background-color: #050811; color: #E2E8F0;")
        right_layout.addWidget(self.table_grid)
        splitter.addWidget(right_frame)

        splitter.setSizes([350, 650])
        layout.addWidget(splitter)

        self._load_sample_or_live_schemas()

    def _load_sample_or_live_schemas(self) -> None:
        """Populate default or discovered schemas."""
        # Check if active scan produced schema or create default demonstration schema
        col1 = ColumnSchema(name="id", data_type="INT", is_primary_key=True, is_nullable=False)
        col2 = ColumnSchema(name="username", data_type="VARCHAR(64)", is_primary_key=False, is_nullable=False)
        col3 = ColumnSchema(name="password_hash", data_type="VARCHAR(128)", is_primary_key=False, is_nullable=False)
        col4 = ColumnSchema(name="email", data_type="VARCHAR(128)", is_primary_key=False, is_nullable=True)
        col5 = ColumnSchema(name="role", data_type="VARCHAR(32)", is_primary_key=False, is_nullable=False)

        tbl_users = TableSchema(
            name="users",
            database="app_production",
            columns=[col1, col2, col3, col4, col5],
            estimated_row_count=4,
        )

        col_audit_1 = ColumnSchema(name="audit_id", data_type="INT", is_primary_key=True)
        col_audit_2 = ColumnSchema(name="event_name", data_type="VARCHAR(64)")
        col_audit_3 = ColumnSchema(name="timestamp", data_type="TIMESTAMP")

        tbl_audit = TableSchema(
            name="audit_log",
            database="app_production",
            columns=[col_audit_1, col_audit_2, col_audit_3],
            estimated_row_count=2,
        )

        db = DatabaseSchema(
            name="app_production",
            dbms="PostgreSQL",
            tables=[tbl_users, tbl_audit],
        )

        self.set_schemas([db])

        # Default sample dump for users table
        self.set_table_dump(
            TableDump(
                database="app_production",
                table="users",
                columns=["id", "username", "password_hash", "email", "role"],
                rows=[
                    [1, "admin", "$2a$12$e8Ym2bW...", "admin@example.org", "administrator"],
                    [2, "operator", "$2a$12$K9Lx1pQ...", "operator@example.org", "auditor"],
                    [3, "service_api", "$2a$12$Zv3Rt8m...", "api@example.org", "system"],
                    [4, "guest", "$2a$12$N4Mn7kP...", "guest@example.org", "readonly"],
                ],
                total_rows=4,
            )
        )

    def set_schemas(self, schemas: list[DatabaseSchema]) -> None:
        """Render database schemas into the tree widget."""
        self._schemas = schemas
        self.tree.clear()

        for db in schemas:
            db_item = QTreeWidgetItem(self.tree, [f"🗄️ {db.name}", f"DBMS: {db.dbms or 'Unknown'}"])
            db_item.setData(0, Qt.ItemDataRole.UserRole, ("db", db.name))

            for tbl in db.tables:
                row_txt = f"{tbl.estimated_row_count} rows" if tbl.estimated_row_count is not None else ""
                tbl_item = QTreeWidgetItem(db_item, [f"📋 {tbl.name}", row_txt])
                tbl_item.setData(0, Qt.ItemDataRole.UserRole, ("table", db.name, tbl.name))

                for col in tbl.columns:
                    pk_marker = " 🔑 (PK)" if col.is_primary_key else ""
                    col_item = QTreeWidgetItem(tbl_item, [f"• {col.name}{pk_marker}", col.data_type])
                    col_item.setData(0, Qt.ItemDataRole.UserRole, ("col", db.name, tbl.name, col.name))

            db_item.setExpanded(True)

    def set_table_dump(self, dump: TableDump) -> None:
        """Render a table dump into the preview table grid."""
        self._current_dump = dump
        self.lbl_dump_title.setText(f"Data Dump: {dump.database}.{dump.table} ({dump.row_count} rows)")

        self.table_grid.clear()
        self.table_grid.setColumnCount(len(dump.columns))
        self.table_grid.setHorizontalHeaderLabels(dump.columns)
        self.table_grid.setRowCount(len(dump.rows))

        for row_idx, row in enumerate(dump.rows):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table_grid.setItem(row_idx, col_idx, item)

        self.table_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.lbl_status.setText(f"Loaded {dump.row_count} records from {dump.database}.{dump.table}")

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data[0] == "table":
            db_name, tbl_name = data[1], data[2]
            self.lbl_status.setText(f"Selected table: {db_name}.{tbl_name}")
            # If current dump matches table, keep it, otherwise show message
            if self._current_dump and self._current_dump.table == tbl_name:
                self.set_table_dump(self._current_dump)
            else:
                self.lbl_dump_title.setText(f"Table: {db_name}.{tbl_name} (Ready for extraction)")
        elif data[0] == "col":
            db_name, tbl_name, col_name = data[1], data[2], data[3]
            self.lbl_status.setText(f"Selected column: {db_name}.{tbl_name}.{col_name}")

    def _export_csv(self) -> None:
        if not self._current_dump or not self._current_dump.rows:
            self.lbl_status.setText("No data dump loaded to export.")
            return

        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        csv_file = report_dir / f"{self._current_dump.database}_{self._current_dump.table}_dump.csv"
        csv_file.write_text(self._current_dump.to_csv_string(), encoding="utf-8")
        self.lbl_status.setText(f"Exported CSV dump to {csv_file.absolute()}")
