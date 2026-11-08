"""Đo hiệu năng truy vấn tổng hợp giữa CSDL nguồn (OLTP 3NF) và Kho dữ liệu (Star Schema),
đồng thời xuất kết quả 5 câu hỏi phân tích OLAP ra thư mục output/.

Thực hiện tiêu chí đánh giá mục 4.3 của Đề cương:
  "Hiệu năng: so sánh thời gian truy vấn tổng hợp trên kho (star schema) với truy vấn trực tiếp
   trên CSDL nguồn ở quy mô từ 100.000 dòng."
"""
from __future__ import annotations

import time
import pandas as pd
from sqlalchemy import text

from common.db import DW_DB, OUTPUT_DIR, SOURCE_DB, SQL_DIR, get_engine, split_sql_script

BENCHMARK_QUERIES = [
    (
        "Q1_TyLeRotTheoKhoaMonHocKy",
        "Tỷ lệ đạt/rớt và điểm TB theo Khoa, Môn học, Năm học (trên ~225.000 dòng)",
        # Truy vấn trực tiếp trên OLTP 3NF (phải JOIN 5 bảng + tự tính lại điểm tổng kết & kết quả đạt)
        """
        SELECT k.ten_khoa, mh.ten_mon, hk.nam_hoc,
               COUNT(*) AS so_luot,
               ROUND(AVG(0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi), 2) AS diem_tb,
               ROUND(100.0 * AVG(CASE WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 4.0 THEN 1 ELSE 0 END), 2) AS ty_le_dat
        FROM DangKyHocPhan dk
        INNER JOIN LopHocPhan lhp ON dk.ma_lhp = lhp.ma_lhp
        INNER JOIN MonHoc mh      ON lhp.ma_mon = mh.ma_mon
        INNER JOIN Khoa k         ON mh.ma_khoa = k.ma_khoa
        INNER JOIN HocKy hk       ON lhp.ma_hoc_ky = hk.ma_hoc_ky
        WHERE dk.diem_qua_trinh BETWEEN 0 AND 10
          AND dk.diem_thi BETWEEN 0 AND 10
        GROUP BY k.ten_khoa, mh.ten_mon, hk.nam_hoc
        """,
        # Truy vấn trên Kho dữ liệu Star Schema (JOIN khóa nguyên surrogate key, điểm/kết quả đã tính sẵn)
        """
        SELECT mh.ten_khoa, mh.ten_mon, tg.nam_hoc,
               COUNT(*) AS so_luot,
               ROUND(AVG(kq.diem_tong_ket), 2) AS diem_tb,
               ROUND(100.0 * AVG(kq.ket_qua_dat), 2) AS ty_le_dat
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_mon_hoc   mh ON kq.mon_hoc_key   = mh.mon_hoc_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        GROUP BY mh.ten_khoa, mh.ten_mon, tg.nam_hoc
        """,
    ),
    (
        "Q2_KetQuaTheoKhoaNganhHocKy",
        "Điểm trung bình hệ 10, hệ 4 và tỷ lệ đạt theo Khoa, Ngành và Năm học",
        # OLTP 3NF: phải nối DangKyHocPhan -> LopHocPhan -> HocKy -> SinhVien -> Nganh -> Khoa + CASE quy đổi hệ 4
        """
        SELECT k.ten_khoa, n.ten_nganh, hk.nam_hoc,
               COUNT(*) AS so_luot,
               ROUND(AVG(0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi), 2) AS diem_tb_10,
               ROUND(AVG(CASE
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 8.5 THEN 4.0
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 8.0 THEN 3.5
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 7.0 THEN 3.0
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 6.5 THEN 2.5
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 5.5 THEN 2.0
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 5.0 THEN 1.5
                   WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 4.0 THEN 1.0
                   ELSE 0.0 END), 2) AS diem_tb_4,
               ROUND(100.0 * AVG(CASE WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 4.0 THEN 1 ELSE 0 END), 2) AS ty_le_dat
        FROM DangKyHocPhan dk
        INNER JOIN LopHocPhan lhp ON dk.ma_lhp = lhp.ma_lhp
        INNER JOIN HocKy hk       ON lhp.ma_hoc_ky = hk.ma_hoc_ky
        INNER JOIN SinhVien sv    ON dk.ma_sv = sv.ma_sv
        INNER JOIN Nganh n        ON sv.ma_nganh = n.ma_nganh
        INNER JOIN Khoa k         ON n.ma_khoa = k.ma_khoa
        WHERE dk.diem_qua_trinh BETWEEN 0 AND 10
          AND dk.diem_thi BETWEEN 0 AND 10
        GROUP BY k.ten_khoa, n.ten_nganh, hk.nam_hoc
        """,
        # Star Schema DW: dim_nganh đã phi chuẩn hóa tên khoa, fact đã tính sẵn diem_he_4 và ket_qua_dat
        """
        SELECT ng.ten_khoa, ng.ten_nganh, tg.nam_hoc,
               COUNT(*) AS so_luot,
               ROUND(AVG(kq.diem_tong_ket), 2) AS diem_tb_10,
               ROUND(AVG(kq.diem_he_4), 2) AS diem_tb_4,
               ROUND(100.0 * AVG(kq.ket_qua_dat), 2) AS ty_le_dat
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        GROUP BY ng.ten_khoa, ng.ten_nganh, tg.nam_hoc
        """,
    ),
    (
        "Q3_KetQuaTheoGiangVienHocViKhoa",
        "Điểm trung bình và tỷ lệ qua môn theo Khoa, Học vị giảng viên và Loại môn học",
        # OLTP 3NF: phải nối DangKyHocPhan -> LopHocPhan -> GiangVien -> Khoa -> MonHoc
        """
        SELECT k.ten_khoa, gv.hoc_vi, mh.loai_mon,
               COUNT(*) AS so_luot,
               ROUND(AVG(0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi), 2) AS diem_tb,
               ROUND(100.0 * AVG(CASE WHEN (0.4 * dk.diem_qua_trinh + 0.6 * dk.diem_thi) >= 4.0 THEN 1 ELSE 0 END), 2) AS ty_le_dat
        FROM DangKyHocPhan dk
        INNER JOIN LopHocPhan lhp ON dk.ma_lhp = lhp.ma_lhp
        INNER JOIN GiangVien gv   ON lhp.ma_gv = gv.ma_gv
        INNER JOIN Khoa k         ON gv.ma_khoa = k.ma_khoa
        INNER JOIN MonHoc mh      ON lhp.ma_mon = mh.ma_mon
        WHERE dk.diem_qua_trinh BETWEEN 0 AND 10
          AND dk.diem_thi BETWEEN 0 AND 10
        GROUP BY k.ten_khoa, gv.hoc_vi, mh.loai_mon
        """,
        # Star Schema DW
        """
        SELECT gv.ten_khoa, gv.hoc_vi, mh.loai_mon,
               COUNT(*) AS so_luot,
               ROUND(AVG(kq.diem_tong_ket), 2) AS diem_tb,
               ROUND(100.0 * AVG(kq.ket_qua_dat), 2) AS ty_le_dat
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_giang_vien gv ON kq.giang_vien_key = gv.giang_vien_key
        INNER JOIN dim_mon_hoc    mh ON kq.mon_hoc_key    = mh.mon_hoc_key
        GROUP BY gv.ten_khoa, gv.hoc_vi, mh.loai_mon
        """,
    ),
]


def _measure_ms(conn, sql: str, repeat: int = 3) -> float:
    # Chạy làm nóng 1 lần, sau đó lấy trung bình repeat lần chạy
    conn.execute(text(sql)).fetchall()
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        conn.execute(text(sql)).fetchall()
        times.append((time.perf_counter() - t0) * 1000.0)
    return round(sum(times) / len(times), 2)


def main() -> None:
    src = get_engine(SOURCE_DB)
    dw = get_engine(DW_DB)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. Xuất kết quả các câu hỏi OLAP trong 05_olap_queries.sql
    stmts = [
        s for s in split_sql_script((SQL_DIR / "05_olap_queries.sql").read_text(encoding="utf-8"))
        if not s.upper().startswith("USE ")
    ]
    names = [
        "olap_q1a_rollup_khoa_mon",
        "olap_q1b_top15_mon_rot_cao",
        "olap_q1c_drilldown_namhoc_hocky",
        "olap_q2_dice_nganh_phuongthuc",
        "olap_q3_tuong_quan_dau_vao_hk1",
        "olap_q4_xu_huong_tuyen_sinh",
        "olap_q5_ket_qua_theo_tinh_thanh",
    ]
    with dw.connect() as dconn:
        for name, stmt in zip(names, stmts):
            df = pd.read_sql(text(stmt), dconn)
            df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
            print(f"\n--- {name} ({len(df)} dòng, hiển thị 8 dòng đầu) ---")
            print(df.head(8).to_string(index=False))

    # 2. So sánh hiệu năng OLTP 3NF vs DW Star Schema
    bench_rows = []
    with src.connect() as sconn, dw.connect() as dconn:
        for code, desc, sql_oltp, sql_dw in BENCHMARK_QUERIES:
            ms_oltp = _measure_ms(sconn, sql_oltp)
            ms_dw = _measure_ms(dconn, sql_dw)
            speedup = round(ms_oltp / max(ms_dw, 0.01), 2)
            bench_rows.append({
                "ma_truy_van": code,
                "mo_ta": desc,
                "thoi_gian_oltp_ms": ms_oltp,
                "thoi_gian_dw_star_ms": ms_dw,
                "tang_toc_lan": speedup,
            })

    df_bench = pd.DataFrame(bench_rows)
    df_bench.to_csv(OUTPUT_DIR / "benchmark_result.csv", index=False, encoding="utf-8-sig")
    print("\n=== SO SÁNH HIỆU NĂNG TRUY VẤN: OLTP (3NF) vs KHO DỮ LIỆU (STAR SCHEMA) ===")
    print(df_bench.to_string(index=False))


if __name__ == "__main__":
    main()

