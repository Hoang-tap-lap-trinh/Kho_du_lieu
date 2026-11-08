"""ETL & Quality Model: Quản lý siêu dữ liệu ETL Log, Data Quality, Rejects và kết quả Test."""
from __future__ import annotations

import pandas as pd
from common.db import OUTPUT_DIR
from mvc.models.base import dw_engine, query_records
from tests.run_dq_tests import main as run_dq_tests_main


def get_etl_and_quality_data() -> dict:
    """Lấy dữ liệu etl_log, etl_data_quality, etl_reject, 10 Test Cases và Benchmark."""
    latest_run = query_records(dw_engine, "SELECT run_id FROM etl_log ORDER BY log_id DESC LIMIT 1")
    run_id = latest_run[0]["run_id"] if latest_run else ""

    etl_log = query_records(dw_engine, """
        SELECT buoc, bang, so_dong_doc, so_dong_nap, so_dong_loai, ghi_chu, bat_dau, ket_thuc
        FROM etl_log
        WHERE run_id = :r
        ORDER BY log_id
    """, {"r": run_id})

    dq = query_records(dw_engine, """
        SELECT bang, loai_kiem_tra, so_dong_truoc, so_dong_sau, cach_xu_ly
        FROM etl_data_quality
        WHERE run_id = :r
        ORDER BY dq_id
    """, {"r": run_id})

    reject_summary = query_records(dw_engine, """
        SELECT bang, ma_loi, COUNT(*) AS so_luong
        FROM etl_reject
        WHERE run_id = :r
        GROUP BY bang, ma_loi
        ORDER BY so_luong DESC
    """, {"r": run_id})

    reject_samples = query_records(dw_engine, """
        SELECT bang, khoa_nguon, ma_loi, mo_ta
        FROM etl_reject
        WHERE run_id = :r
        ORDER BY reject_id
        LIMIT 100
    """, {"r": run_id})

    tc_path = OUTPUT_DIR / "test_cases_result.csv"
    test_cases = pd.read_csv(tc_path).to_dict(orient="records") if tc_path.exists() else []

    bm_path = OUTPUT_DIR / "benchmark_result.csv"
    benchmarks = pd.read_csv(bm_path).to_dict(orient="records") if bm_path.exists() else []

    return {
        "run_id": run_id,
        "etl_log": etl_log,
        "data_quality": dq,
        "reject_summary": reject_summary,
        "reject_samples": reject_samples,
        "test_cases": test_cases,
        "benchmarks": benchmarks,
    }


def execute_test_suite() -> None:
    """Kích hoạt chạy lại 10 Test Cases kiểm thử chất lượng dữ liệu."""
    run_dq_tests_main()

