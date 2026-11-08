"""OLAP Controller: Tiếp nhận bộ lọc đa chiều từ HTTP Request và gọi OLAP Model."""
from __future__ import annotations

from mvc.models.olap_model import get_filter_options, get_overview_data
from mvc.views.view import render_json


class OlapController:
    @staticmethod
    def handle_get_filters() -> tuple[bytes, str]:
        data = get_filter_options()
        return render_json(data)

    @staticmethod
    def handle_get_overview(params: dict) -> tuple[bytes, str]:
        data = get_overview_data(params)
        return render_json(data)

