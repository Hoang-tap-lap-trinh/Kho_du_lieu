"""SCD2 Controller: Điều phối thao tác tra cứu và mô phỏng đổi ngành SCD loại 2."""
from __future__ import annotations

from mvc.models.scd2_model import (
    get_student_scd2_detail,
    search_students,
    simulate_scd2_change,
)
from mvc.views.view import render_json


class Scd2Controller:
    @staticmethod
    def handle_search(params: dict) -> tuple[bytes, str]:
        query = params.get("q", "").strip()
        data = search_students(query)
        return render_json(data)

    @staticmethod
    def handle_get_detail(params: dict) -> tuple[bytes, str]:
        ma_sv = params.get("ma_sv", "19IT001").strip().upper()
        data = get_student_scd2_detail(ma_sv)
        return render_json(data)

    @staticmethod
    def handle_change_major(payload: dict) -> tuple[bytes, str]:
        data = simulate_scd2_change(payload)
        return render_json(data)

