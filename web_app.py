"""Ứng dụng Web tương tác cho Kho dữ liệu Giáo dục VKU (Kiến trúc MVC).

Tổ chức theo mô hình MVC:
  - Model: mvc/models/ (olap_model.py, scd2_model.py, etl_model.py, sql_model.py)
  - View:  mvc/views/ (view.py, web/index.html)
  - Controller: mvc/controllers/ (olap_controller.py, scd2_controller.py, etl_controller.py, sql_controller.py, router.py)

Khởi động server:
    .venv\\Scripts\\python.exe web_app.py
Truy cập tại: http://localhost:8050
"""
from __future__ import annotations

from http.server import ThreadingHTTPServer

# Re-export các thành phần nghiệp vụ để tương thích ngược với web/build_standalone.py và các script khác
from mvc.controllers.router import MvcRouter
from mvc.models.base import json_default_serializer as _json_default
from mvc.models.etl_model import get_etl_and_quality_data
from mvc.models.olap_model import get_filter_options, get_overview_data
from mvc.models.scd2_model import get_student_scd2_detail, simulate_scd2_change
from mvc.views.view import WEB_DIR

PORT = 8050
DashboardHandler = MvcRouter  # Alias tương thích ngược


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), MvcRouter)
    print("=" * 75)
    print("KHO DỮ LIỆU GIÁO DỤC VKU – WEB DASHBOARD (MÔ HÌNH MVC)")
    print(f"Server đang lắng nghe tại: http://localhost:{PORT}")
    print("Nhấn Ctrl+C để dừng server.")
    print("=" * 75)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng Web Server.")
        server.server_close()


if __name__ == "__main__":
    main()
