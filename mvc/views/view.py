"""View Presenter: Phụ trách định dạng đầu ra (HTML giao diện hoặc JSON phản hồi API)."""
from __future__ import annotations

import json
from pathlib import Path
from mvc.models.base import json_default_serializer

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def render_html_page(filename: str = "index.html") -> tuple[bytes, str]:
    """Đọc và trả về nội dung trang Web HTML cùng Content-Type."""
    file_path = WEB_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file giao diện: {file_path}")
    return file_path.read_bytes(), "text/html; charset=utf-8"


def render_json(data: dict | list) -> tuple[bytes, str]:
    """Chuyển đổi dữ liệu từ Controller/Model thành chuỗi JSON nhị phân."""
    body = json.dumps(data, ensure_ascii=False, default=json_default_serializer).encode("utf-8")
    return body, "application/json; charset=utf-8"


def render_error(message: str, status_code: int = 400) -> tuple[bytes, str, int]:
    """Tạo phản hồi JSON báo lỗi cho Controller."""
    body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
    return body, "application/json; charset=utf-8", status_code

