"""Base Model: Khởi tạo kết nối CSDL và các tiện ích thực thi truy vấn."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import text
from common.db import DW_DB, SOURCE_DB, get_engine

src_engine = get_engine(SOURCE_DB)
dw_engine = get_engine(DW_DB)


def json_default_serializer(obj):
    """Xử lý serialization JSON cho các kiểu dữ liệu ngày tháng và Decimal của CSDL."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


def query_records(engine, sql: str, params: dict | None = None) -> list[dict]:
    """Thực thi câu lệnh SQL đọc và trả về danh sách các bản ghi dictionary."""
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        cols = list(result.keys())
        return [dict(zip(cols, row)) for row in result.fetchall()]

