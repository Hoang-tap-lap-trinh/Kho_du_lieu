"""Bước 1 của ETL: Extract dữ liệu thô từ CSDL nguồn (edu_source) sang staging (edu_dw)."""
from __future__ import annotations

from datetime import datetime
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

BANG_NGUON = [
    "Khoa",
    "Nganh",
    "PhuongThucXetTuyen",
    "GiangVien",
    "MonHoc",
    "HocKy",
    "SinhVien",
    "LichSuChuyenNganh",
    "LopHocPhan",
    "DangKyHocPhan",
    "HoSoTuyenSinh",
]


def ghi_log(
    dw_engine: Engine,
    run_id: str,
    buoc: str,
    bang: str,
    so_dong_doc: int,
    so_dong_nap: int,
    so_dong_loai: int,
    bat_dau: datetime,
    ghi_chu: str = "",
) -> None:
    log_df = pd.DataFrame([{
        "run_id": run_id,
        "buoc": buoc,
        "bang": bang,
        "so_dong_doc": int(so_dong_doc),
        "so_dong_nap": int(so_dong_nap),
        "so_dong_loai": int(so_dong_loai),
        "ghi_chu": ghi_chu[:500],
        "bat_dau": bat_dau,
        "ket_thuc": datetime.now(),
    }])
    log_df.to_sql("etl_log", dw_engine, if_exists="append", index=False)


def extract_all(source_engine: Engine, dw_engine: Engine, run_id: str, copy_raw_to_dw: bool = True) -> dict[str, pd.DataFrame]:
    """Đọc toàn bộ bảng từ CSDL nguồn vào bộ nhớ và (tuỳ chọn) lưu bản sao stg_raw_* trong kho."""
    raw: dict[str, pd.DataFrame] = {}
    for ten in BANG_NGUON:
        t0 = datetime.now()
        with source_engine.connect() as conn:
            df = pd.read_sql(text(f"SELECT * FROM {ten}"), conn)
        raw[ten] = df
        if copy_raw_to_dw:
            stg_name = f"stg_raw_{ten.lower()}"
            df.to_sql(stg_name, dw_engine, if_exists="replace", index=False, chunksize=1000, method="multi")
        ghi_log(
            dw_engine,
            run_id=run_id,
            buoc="EXTRACT",
            bang=ten,
            so_dong_doc=len(df),
            so_dong_nap=len(df),
            so_dong_loai=0,
            bat_dau=t0,
            ghi_chu="Đọc từ edu_source vào staging",
        )
    return raw

