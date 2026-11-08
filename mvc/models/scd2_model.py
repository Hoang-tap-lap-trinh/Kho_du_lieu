"""SCD2 Model: Quản lý thông tin sinh viên, lịch sử biến động (SCD loại 2) và cập nhật đa chiều."""
from __future__ import annotations

from datetime import date
import pandas as pd
from sqlalchemy import text

from common import reference as ref
from common.db import call_procedure
from etl.transform import (
    chuan_hoa_chuoi_ten,
    chuan_hoa_gioi_tinh,
    chuan_hoa_tinh_thanh,
    xay_dung_phien_ban_scd2,
)
from mvc.models.base import dw_engine, query_records, src_engine


def search_students(query: str) -> list[dict]:
    """Tìm kiếm danh sách sinh viên theo mã SV hoặc họ tên."""
    return query_records(dw_engine, """
        SELECT ma_sv, MAX(ho_ten) AS ho_ten, MAX(ten_nganh) AS ten_nganh,
               COUNT(*) AS so_phien_ban
        FROM dim_sinh_vien
        WHERE sinh_vien_key > 0
          AND (ma_sv LIKE :q OR ho_ten LIKE :q)
        GROUP BY ma_sv
        ORDER BY so_phien_ban DESC, ma_sv
        LIMIT 25
    """, {"q": f"%{query}%"})


def get_student_scd2_detail(ma_sv: str) -> dict:
    """Lấy chi tiết toàn bộ phiên bản SCD2 và lịch sử học tập của sinh viên."""
    ma_sv = ma_sv.strip().upper()
    versions = query_records(dw_engine, """
        SELECT sinh_vien_key, ma_sv, ho_ten, gioi_tinh, nam_sinh, tinh_thanh, vung_mien,
               nam_nhap_hoc, trang_thai, ma_nganh, ten_nganh, ma_khoa, ten_khoa, ma_lop,
               ngay_hieu_luc, ngay_het_han, is_current
        FROM dim_sinh_vien
        WHERE ma_sv = :sv
        ORDER BY ngay_hieu_luc
    """, {"sv": ma_sv})

    semesters = query_records(dw_engine, """
        SELECT tg.nam_hoc, tg.hoc_ky_so, tg.hoc_ky,
               sv.sinh_vien_key, ng.ma_nganh, ng.ten_nganh, sv.ma_lop,
               COUNT(*) AS so_mon,
               SUM(kq.so_tin_chi) AS tong_tin_chi,
               ROUND(AVG(kq.diem_tong_ket), 2) AS diem_tb_he_10,
               ROUND(AVG(kq.diem_he_4), 2) AS diem_tb_he_4,
               SUM(1 - kq.ket_qua_dat) AS so_mon_rot
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE sv.ma_sv = :sv
        GROUP BY tg.nam_hoc, tg.hoc_ky_so, tg.hoc_ky, sv.sinh_vien_key, ng.ma_nganh, ng.ten_nganh, sv.ma_lop
        ORDER BY tg.nam_hoc, tg.hoc_ky_so
    """, {"sv": ma_sv})

    courses = query_records(dw_engine, """
        SELECT tg.nam_hoc, tg.hoc_ky_so, mh.ma_mon, mh.ten_mon, mh.so_tin_chi,
               ng.ma_nganh AS nganh_khi_hoc, sv.sinh_vien_key,
               kq.diem_qua_trinh, kq.diem_thi, kq.diem_tong_ket, kq.diem_chu, kq.diem_he_4, kq.ket_qua_dat
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_mon_hoc   mh ON kq.mon_hoc_key   = mh.mon_hoc_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE sv.ma_sv = :sv
        ORDER BY tg.nam_hoc, tg.hoc_ky_so, mh.ma_mon
    """, {"sv": ma_sv})

    return {"ma_sv": ma_sv, "versions": versions, "semesters": semesters, "courses": courses}


def simulate_scd2_change(payload: dict) -> dict:
    """Thực hiện đổi ngành trực tiếp cho 1 sinh viên ở nguồn và cập nhật SCD2 vào kho."""
    ma_sv = str(payload.get("ma_sv", "")).strip().upper()
    ma_nganh_moi = str(payload.get("ma_nganh_moi", "")).strip().upper()
    ngay_chuyen = str(payload.get("ngay_chuyen", "2021-08-20")).strip()

    cur_rows = query_records(dw_engine, """
        SELECT ma_sv, ho_ten, ma_nganh, ma_lop, nam_nhap_hoc, ngay_hieu_luc
        FROM dim_sinh_vien
        WHERE ma_sv = :sv AND is_current = 1
    """, {"sv": ma_sv})
    if not cur_rows:
        raise ValueError(f"Không tìm thấy sinh viên {ma_sv} trong kho dữ liệu.")

    cur = cur_rows[0]
    if cur["ma_nganh"] == ma_nganh_moi:
        raise ValueError(f"Sinh viên {ma_sv} hiện đang ở ngành {ma_nganh_moi} rồi. Hãy chọn ngành khác.")

    ma_lop_moi = f"{int(cur['nam_nhap_hoc']) % 100:02d}{ma_nganh_moi}1"

    # 1. Cập nhật ở CSDL nguồn edu_source
    with src_engine.begin() as sconn:
        sconn.execute(text("""
            INSERT INTO LichSuChuyenNganh (ma_sv, ma_nganh_cu, ma_nganh_moi, ma_lop_cu, ma_lop_moi, ngay_chuyen)
            VALUES (:sv, :nc, :nm, :lc, :lm, :ngay)
        """), {
            "sv": ma_sv, "nc": cur["ma_nganh"], "nm": ma_nganh_moi,
            "lc": cur["ma_lop"], "lm": ma_lop_moi, "ngay": ngay_chuyen,
        })
        sconn.execute(text("""
            UPDATE SinhVien
            SET ma_nganh = :nm, ma_lop = :lm, ngay_cap_nhat = NOW()
            WHERE ma_sv = :sv
        """), {"nm": ma_nganh_moi, "lm": ma_lop_moi, "sv": ma_sv})

        sv_df = pd.read_sql(text("SELECT * FROM SinhVien WHERE ma_sv = :sv"), sconn, params={"sv": ma_sv})
        ls_df = pd.read_sql(text("SELECT * FROM LichSuChuyenNganh WHERE ma_sv = :sv"), sconn, params={"sv": ma_sv})

    # 2. Chuẩn bị phiên bản SCD2 của sinh viên này và gọi sp_scd2_dim_sinh_vien
    with dw_engine.connect() as dconn:
        dim_nganh_df = pd.read_sql(text("SELECT ma_nganh, ten_nganh, ma_khoa, ten_khoa, he_dao_tao FROM dim_nganh"), dconn)

    sv_df["ma_sv"] = sv_df["ma_sv"].str.strip().str.upper()
    sv_df["ma_nganh"] = sv_df["ma_nganh"].str.strip().str.upper()
    sv_df["ma_lop"] = sv_df["ma_lop"].str.strip().str.upper()
    sv_df["ho_ten"] = chuan_hoa_chuoi_ten(sv_df["ho_ten"])
    sv_df["gioi_tinh"], _ = chuan_hoa_gioi_tinh(sv_df["gioi_tinh"])
    sv_df["tinh_thanh"], _ = chuan_hoa_tinh_thanh(sv_df["tinh_thanh"])
    sv_df["vung_mien"] = sv_df["tinh_thanh"].map(ref.VUNG_MIEN).fillna("Khác")
    sv_df["nam_sinh"] = pd.to_datetime(sv_df["ngay_sinh"]).dt.year

    ver_df = xay_dung_phien_ban_scd2(sv_df, ls_df, dim_nganh_df)
    with dw_engine.begin() as dconn:
        dconn.execute(text("DELETE FROM stg_sinh_vien_version WHERE ma_sv = :sv"), {"sv": ma_sv})
    ver_df.to_sql("stg_sinh_vien_version", dw_engine, if_exists="append", index=False)
    call_procedure(dw_engine, "sp_scd2_dim_sinh_vien")

    # 3. Cập nhật lại khóa sinh_vien_key và nganh_key cho các dòng fact của sinh viên này theo ngày hiệu lực SCD2
    with dw_engine.begin() as dconn:
        dconn.execute(text("""
            UPDATE fact_ket_qua_hoc_tap kq
            INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
            INNER JOIN dim_sinh_vien sv_old ON kq.sinh_vien_key = sv_old.sinh_vien_key
            INNER JOIN dim_sinh_vien sv_new
                ON sv_new.ma_sv = sv_old.ma_sv
               AND tg.ngay BETWEEN sv_new.ngay_hieu_luc AND sv_new.ngay_het_han
            INNER JOIN dim_nganh ng ON ng.ma_nganh = sv_new.ma_nganh
            SET kq.sinh_vien_key = sv_new.sinh_vien_key,
                kq.nganh_key     = ng.nganh_key
            WHERE sv_old.ma_sv = :sv
        """), {"sv": ma_sv})

    return get_student_scd2_detail(ma_sv)

