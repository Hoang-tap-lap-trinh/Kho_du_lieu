"""Điều phối toàn bộ quy trình ETL: Extract -> Transform -> Load.

Cách chạy:
    python -m etl.pipeline --init-dw   # tạo mới kho edu_dw + stored procedures + OLAP views rồi chạy ETL
    python -m etl.pipeline             # chạy lại ETL tăng trưởng / kiểm tra idempotent trên kho hiện có
"""
from __future__ import annotations

import argparse
import time
import uuid
import pandas as pd
from sqlalchemy import text

from common.db import DW_DB, OUTPUT_DIR, SOURCE_DB, SQL_DIR, get_engine, run_sql_file
from etl.extract import extract_all
from etl.load import load_all
from etl.transform import transform_all


def run_etl(init_dw: bool = False, copy_raw_to_dw: bool = True) -> str:
    t0 = time.time()
    run_id = uuid.uuid4().hex[:12]

    server_engine = get_engine()
    if init_dw:
        print("[INIT] Tạo schema kho dữ liệu edu_dw và các Stored Procedure...")
        run_sql_file(server_engine, SQL_DIR / "02_create_dw.sql")
        dw_engine = get_engine(DW_DB)
        run_sql_file(dw_engine, SQL_DIR / "03_procedures.sql")
        if (SQL_DIR / "04_olap_views.sql").exists():
            run_sql_file(dw_engine, SQL_DIR / "04_olap_views.sql")
    else:
        dw_engine = get_engine(DW_DB)

    source_engine = get_engine(SOURCE_DB)

    print(f"[1/3] EXTRACT từ {SOURCE_DB} (run_id={run_id})...")
    raw = extract_all(source_engine, dw_engine, run_id, copy_raw_to_dw=False)

    print("[2/3] TRANSFORM (chuẩn hóa, loại trùng, xử lý điểm lỗi, chuẩn bị SCD2)...")
    transformed = transform_all(raw, dw_engine, run_id)

    print(f"[3/3] LOAD vào {DW_DB} (Dimension trước, Fact sau)...")
    summary = load_all(transformed, dw_engine, run_id)

    OUTPUT_DIR.mkdir(exist_ok=True)
    with dw_engine.connect() as conn:
        df_log = pd.read_sql(
            text("SELECT buoc, bang, so_dong_doc, so_dong_nap, so_dong_loai, ghi_chu "
                 "FROM etl_log WHERE run_id = :r ORDER BY log_id"),
            conn, params={"r": run_id},
        )
        df_dq = pd.read_sql(
            text("SELECT bang, loai_kiem_tra, so_dong_truoc, so_dong_sau, cach_xu_ly "
                 "FROM etl_data_quality WHERE run_id = :r ORDER BY dq_id"),
            conn, params={"r": run_id},
        )
    df_log.to_csv(OUTPUT_DIR / "etl_log_latest.csv", index=False, encoding="utf-8-sig")
    df_dq.to_csv(OUTPUT_DIR / "etl_data_quality_latest.csv", index=False, encoding="utf-8-sig")

    print("\n=== BẢNG LOG ETL (etl_log) ===")
    print(df_log.to_string(index=False))
    print("\n=== BẢNG SO SÁNH TRƯỚC & SAU KHI LÀM SẠCH (etl_data_quality) ===")
    print(df_dq.to_string(index=False))
    print(f"\nHoàn tất ETL (run_id={run_id}) trong {time.time() - t0:.1f} giây. Tóm tắt: {summary}")
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Chạy quy trình ETL cho kho dữ liệu giáo dục")
    parser.add_argument("--init-dw", action="store_true", help="Tạo lại schema edu_dw trước khi chạy ETL")
    args = parser.parse_args()
    run_etl(init_dw=args.init_dw)


if __name__ == "__main__":
    main()
