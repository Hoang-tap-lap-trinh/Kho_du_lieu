"""ETL & Quality Controller: Phục vụ dữ liệu kiểm soát chất lượng và kích hoạt Test suite."""
from __future__ import annotations

from mvc.models.etl_model import execute_test_suite, get_etl_and_quality_data
from mvc.views.view import render_json


class EtlController:
    @staticmethod
    def handle_get_data() -> tuple[bytes, str]:
        data = get_etl_and_quality_data()
        return render_json(data)

    @staticmethod
    def handle_run_tests() -> tuple[bytes, str]:
        execute_test_suite()
        data = get_etl_and_quality_data()
        return render_json(data)

