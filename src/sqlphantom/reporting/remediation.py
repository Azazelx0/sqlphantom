"""Defensive Remediation Assistant for SQLPhantom.

Provides framework-specific parameterized query templates, ORM recommendations,
and secure coding patterns for addressing SQL injection vulnerabilities in accordance
with OWASP ASVS v4.0.3 (V5.3) and CWE-89 (SQL Injection).
"""

from __future__ import annotations

from typing import Any
from sqlphantom.domain.models import Finding


class RemediationAssistant:
    """Generates defensive remediation guidance and parameterized query snippets."""

    @staticmethod
    def get_cwe_details() -> dict[str, str]:
        """Return standardized CWE and OWASP metadata."""
        return {
            "cwe_id": "CWE-89",
            "cwe_title": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
            "owasp_top_10": "A03:2021 – Injection",
            "owasp_asvs": "V5.3.1 - Verify that parameterized queries or ORMs are used for all database queries.",
            "severity": "CRITICAL",
        }

    @classmethod
    def generate_snippets(cls, finding: Finding) -> dict[str, str]:
        """Generate defensive code templates for fixing the vulnerability in different languages."""
        param = finding.parameter or "user_id"
        table = "accounts"
        column = param if param not in ("*", "") else "id"

        return {
            "python_psycopg": cls._python_psycopg_template(table, column, param),
            "python_sqlalchemy": cls._python_sqlalchemy_template(table, column, param),
            "nodejs_pg": cls._nodejs_pg_template(table, column, param),
            "java_jdbc": cls._java_jdbc_template(table, column, param),
            "php_pdo": cls._php_pdo_template(table, column, param),
            "csharp_ef": cls._csharp_ef_template(table, column, param),
        }

    @staticmethod
    def _python_psycopg_template(table: str, column: str, param: str) -> str:
        return f'''# Python (psycopg2 / psycopg3) Parameterized Query
# NEVER format or concatenate strings into queries.
# Use %s positional placeholders and pass arguments as a separate tuple.

import psycopg2

def get_record(conn, {param}_value):
    query = """
        SELECT *
        FROM {table}
        WHERE {column} = %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, ({param}_value,))
        return cursor.fetchall()
'''

    @staticmethod
    def _python_sqlalchemy_template(table: str, column: str, param: str) -> str:
        return f'''# Python (SQLAlchemy Core / ORM) Parameterized Query
# Use bound parameters with text() or high-level ORM filter queries.

from sqlalchemy import text
from sqlalchemy.orm import Session

def get_record(session: Session, {param}_value):
    stmt = text("SELECT * FROM {table} WHERE {column} = :param_val")
    result = session.execute(stmt, {{"param_val": {param}_value}})
    return result.fetchall()
'''

    @staticmethod
    def _nodejs_pg_template(table: str, column: str, param: str) -> str:
        return f'''// Node.js (node-postgres / pg)
// Use parameterized queries with $1, $2 indexed placeholders.

import {{ Client }} from 'pg';

async function getRecord(client, {param}Value) {{
    const query = `
        SELECT *
        FROM {table}
        WHERE {column} = $1;
    `;
    const res = await client.query(query, [{param}Value]);
    return res.rows;
}}
'''

    @staticmethod
    def _java_jdbc_template(table: str, column: str, param: str) -> str:
        return f'''// Java (JDBC PreparedStatement)
// Use java.sql.PreparedStatement with '?' placeholders.

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SecurityFix {{
    public static void queryRecord(Connection conn, String {param}Value) throws SQLException {{
        String sql = "SELECT * FROM {table} WHERE {column} = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {{
            stmt.setString(1, {param}Value);
            try (ResultSet rs = stmt.executeQuery()) {{
                while (rs.next()) {{
                    // Process results securely
                }}
            }}
        }}
    }}
}}
'''

    @staticmethod
    def _php_pdo_template(table: str, column: str, param: str) -> str:
        return f'''<?php
// PHP (PDO Prepared Statements)
// Always use PDO::prepare with named or positional parameters.

function getRecord(PDO $pdo, string ${param}Value): array {{
    $sql = "SELECT * FROM {table} WHERE {column} = :param";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([':param' => ${param}Value]);
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}}
'''

    @staticmethod
    def _csharp_ef_template(table: str, column: str, param: str) -> str:
        return f'''// C# (.NET Entity Framework Core)
// Use LINQ with parameterized interpolation (FromSqlInterpolated).

using Microsoft.EntityFrameworkCore;

public async Task<List<Account>> GetRecordAsync(MyDbContext context, string {param}Value)
{{
    // EF Core handles parameterization automatically with interpolated strings:
    return await context.Accounts
        .FromSqlInterpolated($"SELECT * FROM {table} WHERE {column} = {{{param}Value}}")
        .ToListAsync();
}}
'''
