"""Database Schema and Table Dump Domain Models.

Provides models for structured database schemas, extracted tables, columns,
and virtualized table dump representations.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    """Schema definition for a relational database column."""

    name: str
    data_type: str = "VARCHAR"
    is_primary_key: bool = False
    is_nullable: bool = True


class TableSchema(BaseModel):
    """Schema definition for a relational database table."""

    name: str
    database: str = ""
    columns: list[ColumnSchema] = Field(default_factory=list)
    estimated_row_count: int | None = None

    @property
    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]


class DatabaseSchema(BaseModel):
    """Extracted schema of a database with tables."""

    name: str
    dbms: str = ""
    tables: list[TableSchema] = Field(default_factory=list)

    @property
    def table_count(self) -> int:
        return len(self.tables)

    def get_table(self, table_name: str) -> TableSchema | None:
        for t in self.tables:
            if t.name.lower() == table_name.lower():
                return t
        return None


class TableDump(BaseModel):
    """Structured representation of extracted table rows for virtualized grid rendering."""

    database: str
    table: str
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    total_rows: int = 0

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def to_csv_string(self) -> str:
        """Export table dump to CSV text format."""
        import csv
        import io

        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(self.columns)
        for r in self.rows:
            writer.writerow(r)
        return out.getvalue()
