"""SQL Model: Thực thi truy vấn SQL tương tác an toàn trên kho hoặc nguồn."""
from __future__ import annotations

from mvc.models.base import dw_engine, query_records, src_engine


def run_custom_query(db_choice: str, sql_stmt: str) -> dict:
    """Thực thi câu truy vấn đọc an toàn (SELECT, WITH, SHOW, EXPLAIN)."""
    sql_stmt = sql_stmt.strip()
    if not sql_stmt.upper().startswith(("SELECT", "SHOW", "DESC", "EXPLAIN", "WITH")):
        raise ValueError("Chỉ cho phép thực thi câu lệnh truy vấn đọc (SELECT / WITH / SHOW / EXPLAIN).")

    eng = dw_engine if db_choice == "dw" else src_engine
    rows = query_records(eng, sql_stmt)
    return {
        "rows": rows[:500],
        "total_returned": len(rows),
    }

