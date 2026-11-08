"""HTTP Router: Tiếp nhận HTTP Request (GET/POST), phân luồng đến các Controller tương ứng và trả View."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from mvc.controllers.etl_controller import EtlController
from mvc.controllers.olap_controller import OlapController
from mvc.controllers.scd2_controller import Scd2Controller
from mvc.controllers.sql_controller import SqlController
from mvc.views.view import render_error, render_html_page


class MvcRouter(BaseHTTPRequestHandler):
    def _respond(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = {k: v[0] for k, v in parse_qs(parsed.query).items() if v and v[0]}

        try:
            # 1. View Giao diện chính (HTML)
            if path in ("/", "/index.html"):
                body, ct = render_html_page("index.html")
                self._respond(body, ct, 200)
                return

            # 2. OLAP Endpoints
            if path == "/api/filters":
                body, ct = OlapController.handle_get_filters()
                self._respond(body, ct, 200)
                return

            if path == "/api/overview":
                body, ct = OlapController.handle_get_overview(qs)
                self._respond(body, ct, 200)
                return

            # 3. SCD2 Endpoints
            if path == "/api/student":
                body, ct = Scd2Controller.handle_get_detail(qs)
                self._respond(body, ct, 200)
                return

            if path == "/api/search_student":
                body, ct = Scd2Controller.handle_search(qs)
                self._respond(body, ct, 200)
                return

            # 4. ETL & Data Quality Endpoints
            if path == "/api/etl":
                body, ct = EtlController.handle_get_data()
                self._respond(body, ct, 200)
                return

            body, ct, st = render_error(f"Không tìm thấy tài nguyên: {path}", 404)
            self._respond(body, ct, st)

        except Exception as exc:
            body, ct, st = render_error(str(exc), 500)
            self._respond(body, ct, st)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"

        try:
            payload = json.loads(raw_body or "{}")

            # 1. SCD2 Đổi ngành
            if path == "/api/scd2_change":
                body, ct = Scd2Controller.handle_change_major(payload)
                self._respond(body, ct, 200)
                return

            # 2. Chạy lại Test Cases
            if path == "/api/run_tests":
                body, ct = EtlController.handle_run_tests()
                self._respond(body, ct, 200)
                return

            # 3. Chạy câu lệnh SQL
            if path == "/api/sql":
                body, ct = SqlController.handle_execute_sql(payload)
                self._respond(body, ct, 200)
                return

            body, ct, st = render_error(f"Endpoint không hợp lệ: {path}", 404)
            self._respond(body, ct, st)

        except Exception as exc:
            body, ct, st = render_error(str(exc), 400)
            self._respond(body, ct, st)

    def log_message(self, format: str, *args) -> None:
        # Tắt in log request để terminal gọn gàng
        return

