"""
Unit tests for Database Schema and Table Dump models.
"""

from sqlphantom.domain.schema import ColumnSchema, TableSchema, DatabaseSchema, TableDump


def test_schema_hierarchy():
    col1 = ColumnSchema(name="id", data_type="INTEGER", is_primary_key=True, is_nullable=False)
    col2 = ColumnSchema(name="username", data_type="VARCHAR(64)", is_primary_key=False, is_nullable=False)
    col3 = ColumnSchema(name="email", data_type="VARCHAR(128)", is_primary_key=False, is_nullable=True)

    tbl = TableSchema(name="users", database="production", columns=[col1, col2, col3], estimated_row_count=100)
    assert tbl.column_names == ["id", "username", "email"]

    db = DatabaseSchema(name="production", dbms="PostgreSQL", tables=[tbl])
    assert db.table_count == 1
    assert db.get_table("users") is not None
    assert db.get_table("nonexistent") is None


def test_table_dump_csv_export():
    dump = TableDump(
        database="app_db",
        table="audit_log",
        columns=["id", "action", "status"],
        rows=[
            [1, "login", "success"],
            [2, "password_reset", "requested"],
        ],
        total_rows=2,
    )

    assert dump.row_count == 2
    csv_str = dump.to_csv_string()
    assert "id,action,status" in csv_str
    assert "1,login,success" in csv_str
    assert "2,password_reset,requested" in csv_str
