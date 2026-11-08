"""SQL Controller: Tiếp nhận và xác thực câu truy vấn SQL tùy chỉnh từ client."""
from __future__ import annotations

from mvc.models.sql_model import run_custom_query
from mvc.views.view import render_json


class SqlController:
    @staticmethod
    def handle_execute_sql(payload: dict) -> tuple[bytes, str]:
        db_choice = payload.get("db", "dw")
        sql_stmt = str(payload.get("sql", "")).strip()
        data = run_custom_query(db_choice, sql_stmt)
        return render_json(data)

