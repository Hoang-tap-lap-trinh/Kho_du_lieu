"""Bước 3 của ETL: Load dữ liệu đã làm sạch vào các bảng Dimension (SCD1/SCD2) và Fact."""
from __future__ import annotations

from datetime import datetime
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from common.db import call_procedure
from etl.extract import ghi_log


def _upsert_dataframe(dw_engine: Engine, table: str, df: pd.DataFrame, update_cols: list[str]) -> None:
    """Nạp dữ liệu vào bảng Dimension theo cơ chế INSERT ... ON DUPLICATE KEY UPDATE."""
    if df.empty:
        return
    cols = list(df.columns)
    col_list = ", ".join(cols)
    placeholders = ", ".join([f":{c}" for c in cols])
    updates = ", ".join([f"{c} = VALUES({c})" for c in update_cols])
    sql = text(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}")
    records = df.to_dict(orient="records")
    with dw_engine.begin() as conn:
        for i in range(0, len(records), 1000):
            conn.execute(sql, records[i : i + 1000])


def load_all(transformed: dict[str, pd.DataFrame], dw_engine: Engine, run_id: str) -> dict:
    """Nạp tất cả bảng Dimension trước, sau đó nạp 2 bảng Fact qua Stored Procedure."""
    summary: dict = {}

    # 1. Nạp các Dimension tĩnh / SCD1
    dim_specs = [
        ("dim_thoi_gian", transformed["dim_thoi_gian"],
         ["ngay", "ngay_trong_thang", "thang", "quy", "nam", "hoc_ky", "hoc_ky_so", "nam_hoc", "ten_hoc_ky", "la_cuoi_tuan"]),
        ("dim_nganh", transformed["dim_nganh"],
         ["ten_nganh", "ma_khoa", "ten_khoa", "he_dao_tao"]),
        ("dim_mon_hoc", transformed["dim_mon_hoc"],
         ["ten_mon", "so_tin_chi", "loai_mon", "ma_khoa", "ten_khoa"]),
        ("dim_giang_vien", transformed["dim_giang_vien"],
         ["ho_ten", "hoc_vi", "ma_khoa", "ten_khoa"]),
        ("dim_phuong_thuc_xet_tuyen", transformed["dim_ptxt"],
         ["ten_phuong_thuc", "thang_diem", "mo_ta"]),
    ]
    for table, df, upd_cols in dim_specs:
        t0 = datetime.now()
        _upsert_dataframe(dw_engine, table, df, upd_cols)
        ghi_log(dw_engine, run_id, "LOAD", table, len(df), len(df), 0, t0, "Upsert dimension (SCD1)")
        summary[table] = len(df)

    # 2. Nạp dim_sinh_vien theo SCD loại 2 qua Stored Procedure sp_scd2_dim_sinh_vien
    t0 = datetime.now()
    stg_sv = transformed["stg_sinh_vien_version"]
    with dw_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE stg_sinh_vien_version"))
    stg_sv.to_sql("stg_sinh_vien_version", dw_engine, if_exists="append", index=False, chunksize=1000, method="multi")
    scd2_res = call_procedure(dw_engine, "sp_scd2_dim_sinh_vien")
    scd2_info = scd2_res[0] if scd2_res else {"so_dong_them_moi": 0, "so_dong_cap_nhat": 0, "so_dong_dong_lich_su": 0}
    with dw_engine.connect() as conn:
        tong_dim_sv = int(conn.execute(text("SELECT COUNT(*) FROM dim_sinh_vien WHERE sinh_vien_key > 0")).scalar())
    ghi_log(
        dw_engine, run_id, "LOAD", "dim_sinh_vien", len(stg_sv), tong_dim_sv, 0, t0,
        f"SCD2 proc: thêm mới={scd2_info['so_dong_them_moi']}, đóng lịch sử={scd2_info['so_dong_dong_lich_su']}",
    )
    summary["dim_sinh_vien"] = tong_dim_sv
    summary["scd2_detail"] = scd2_info

    # 3. Nạp fact_ket_qua_hoc_tap
    t0 = datetime.now()
    stg_kq = transformed["stg_fact_ket_qua_hoc_tap"]
    with dw_engine.connect() as conn:
        existing_kq = int(conn.execute(text("SELECT COUNT(*) FROM fact_ket_qua_hoc_tap")).scalar())
    need_full_kq = (
        existing_kq != len(stg_kq)
        or int(scd2_info.get("so_dong_them_moi", 0)) > 0
        or int(scd2_info.get("so_dong_dong_lich_su", 0)) > 0
    )
    if need_full_kq:
        with dw_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE stg_fact_ket_qua_hoc_tap"))
        stg_kq.to_sql("stg_fact_ket_qua_hoc_tap", dw_engine, if_exists="append", index=False, chunksize=1000, method="multi")
        kq_res = call_procedure(dw_engine, "sp_load_fact_ket_qua_hoc_tap")
        tong_kq = int(kq_res[0]["tong_dong_fact_ket_qua"]) if kq_res else len(stg_kq)
    else:
        tong_kq = existing_kq
    ghi_log(
        dw_engine, run_id, "LOAD", "fact_ket_qua_hoc_tap",
        len(stg_kq), tong_kq, len(stg_kq) - tong_kq, t0,
        "Nạp qua sp_load_fact_ket_qua_hoc_tap (tra cứu khóa SCD2 theo ngày học kỳ)",
    )
    summary["fact_ket_qua_hoc_tap"] = tong_kq

    # 4. Nạp fact_tuyen_sinh
    t0 = datetime.now()
    stg_ts = transformed["stg_fact_tuyen_sinh"]
    with dw_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE stg_fact_tuyen_sinh"))
    stg_ts.to_sql("stg_fact_tuyen_sinh", dw_engine, if_exists="append", index=False, chunksize=1000, method="multi")
    ts_res = call_procedure(dw_engine, "sp_load_fact_tuyen_sinh")
    tong_ts = int(ts_res[0]["tong_dong_fact_tuyen_sinh"]) if ts_res else len(stg_ts)
    ghi_log(
        dw_engine, run_id, "LOAD", "fact_tuyen_sinh",
        len(stg_ts), tong_ts, len(stg_ts) - tong_ts, t0,
        "Nạp qua sp_load_fact_tuyen_sinh",
    )
    summary["fact_tuyen_sinh"] = tong_ts

    return summary

