"""OLAP Model: Xử lý dữ liệu đa chiều, KPI và 5 câu hỏi phân tích quản lý đào tạo."""
from __future__ import annotations

from mvc.models.base import dw_engine, query_records


def get_filter_options() -> dict:
    """Lấy danh mục dữ liệu cho các bộ lọc đa chiều (Khoa, Ngành, Năm học, Vùng miền)."""
    khoa = query_records(dw_engine, "SELECT DISTINCT ma_khoa, ten_khoa FROM dim_nganh ORDER BY ma_khoa")
    nganh = query_records(dw_engine, "SELECT ma_nganh, ten_nganh, ma_khoa FROM dim_nganh ORDER BY ma_nganh")
    nam_hoc = query_records(dw_engine, """
        SELECT DISTINCT tg.nam_hoc
        FROM fact_ket_qua_hoc_tap kq
        JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        ORDER BY tg.nam_hoc
    """)
    vung_mien = query_records(dw_engine, """
        SELECT DISTINCT vung_mien FROM dim_sinh_vien WHERE sinh_vien_key > 0 ORDER BY vung_mien
    """)
    sv_scd2 = query_records(dw_engine, """
        SELECT ma_sv, MAX(ho_ten) AS ho_ten, COUNT(*) AS so_phien_ban
        FROM dim_sinh_vien
        WHERE sinh_vien_key > 0
        GROUP BY ma_sv
        HAVING COUNT(*) > 1
        ORDER BY ma_sv
        LIMIT 50
    """)
    return {
        "khoa": khoa,
        "nganh": nganh,
        "nam_hoc": [r["nam_hoc"] for r in nam_hoc],
        "vung_mien": [r["vung_mien"] for r in vung_mien],
        "sv_scd2": sv_scd2,
    }


def get_overview_data(filters: dict) -> dict:
    """Tổng hợp KPI và dữ liệu cho 5 câu hỏi OLAP theo bộ lọc Slice/Dice của người dùng."""
    where_kq = ["1=1"]
    params: dict = {}

    if filters.get("ma_khoa"):
        where_kq.append("ng.ma_khoa = :ma_khoa")
        params["ma_khoa"] = filters["ma_khoa"]
    if filters.get("ma_nganh"):
        where_kq.append("ng.ma_nganh = :ma_nganh")
        params["ma_nganh"] = filters["ma_nganh"]
    if filters.get("nam_hoc"):
        where_kq.append("tg.nam_hoc = :nam_hoc")
        params["nam_hoc"] = filters["nam_hoc"]
    if filters.get("vung_mien"):
        where_kq.append("sv.vung_mien = :vung_mien")
        params["vung_mien"] = filters["vung_mien"]

    where_sql = " AND ".join(where_kq)

    # 1. KPIs
    kpi = query_records(dw_engine, f"""
        SELECT
            COUNT(kq.ket_qua_id)                          AS tong_luot_hoc_phan,
            COUNT(DISTINCT sv.ma_sv)                      AS tong_sinh_vien,
            ROUND(AVG(kq.diem_tong_ket), 2)               AS diem_tb_he_10,
            ROUND(AVG(kq.diem_he_4), 2)                   AS diem_tb_he_4,
            ROUND(100.0 * AVG(kq.ket_qua_dat), 2)         AS ty_le_dat_pct,
            ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2)     AS ty_le_rot_pct
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE {where_sql}
    """, params)[0]

    kpi_extra = query_records(dw_engine, """
        SELECT
            (SELECT COUNT(*) FROM fact_tuyen_sinh) AS tong_ho_so_tuyen_sinh,
            (SELECT COUNT(*) FROM dim_sinh_vien WHERE sinh_vien_key > 0 AND is_current = 0) AS so_dong_lich_su_scd2,
            (SELECT COUNT(*) FROM etl_reject WHERE run_id = (SELECT run_id FROM etl_log ORDER BY log_id DESC LIMIT 1)) AS so_dong_loi_bi_loai
    """)[0]
    kpi.update(kpi_extra)

    # 2. Q1A: Tỷ lệ rớt & Điểm TB theo Khoa quản lý môn học
    q1_khoa = query_records(dw_engine, f"""
        SELECT
            mh.ma_khoa,
            mh.ten_khoa,
            COUNT(kq.ket_qua_id)                      AS tong_luot_hoc,
            SUM(1 - kq.ket_qua_dat)                   AS so_luot_rot,
            ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2) AS ty_le_rot_pct,
            ROUND(100.0 * AVG(kq.ket_qua_dat), 2)     AS ty_le_dat_pct,
            ROUND(AVG(kq.diem_tong_ket), 2)           AS diem_tb_he_10
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_mon_hoc   mh ON kq.mon_hoc_key   = mh.mon_hoc_key
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE {where_sql}
        GROUP BY mh.ma_khoa, mh.ten_khoa
        ORDER BY ty_le_rot_pct DESC
    """, params)

    # 3. Q1B: Top 15 môn có tỷ lệ rớt cao nhất (có áp dụng bộ lọc)
    q1_top_mon = query_records(dw_engine, f"""
        SELECT
            mh.ma_mon,
            mh.ten_mon,
            mh.ten_khoa,
            mh.loai_mon,
            COUNT(kq.ket_qua_id)                      AS tong_luot_hoc,
            SUM(1 - kq.ket_qua_dat)                   AS so_luot_rot,
            ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2) AS ty_le_rot_pct,
            ROUND(AVG(kq.diem_tong_ket), 2)           AS diem_tb_mon
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_mon_hoc   mh ON kq.mon_hoc_key   = mh.mon_hoc_key
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE {where_sql}
        GROUP BY mh.ma_mon, mh.ten_mon, mh.ten_khoa, mh.loai_mon
        ORDER BY ty_le_rot_pct DESC
        LIMIT 15
    """, params)

    # 4. Q1C: Drill-down theo Năm học & Học kỳ
    q1_hocky = query_records(dw_engine, f"""
        SELECT
            CONCAT(tg.nam_hoc, ' - HK', tg.hoc_ky_so) AS ky_hoc,
            tg.nam_hoc,
            tg.hoc_ky_so,
            COUNT(kq.ket_qua_id)                      AS tong_luot_hoc,
            ROUND(100.0 * AVG(kq.ket_qua_dat), 2)     AS ty_le_dat_pct,
            ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2) AS ty_le_rot_pct,
            ROUND(AVG(kq.diem_tong_ket), 2)           AS diem_tb_he_10
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE {where_sql}
        GROUP BY tg.nam_hoc, tg.hoc_ky_so
        ORDER BY tg.nam_hoc, tg.hoc_ky_so
    """, params)

    # 5. Q2: Dice Ngành x Phương thức xét tuyển
    q2_dice = query_records(dw_engine, """
        SELECT
            ten_nganh,
            ten_phuong_thuc,
            so_sinh_vien,
            so_luot_hoc_phan,
            diem_tb_he_10,
            diem_tb_he_4,
            ty_le_dat_pct
        FROM vw_olap_cube_nganh_phuongthuc
        WHERE ten_nganh <> 'ALL_NGANH' AND ten_phuong_thuc <> 'ALL_PHUONG_THUC'
        ORDER BY ten_nganh, ten_phuong_thuc
    """)

    # 6. Q3: Tương quan Điểm xét tuyển đầu vào vs GPA Học kỳ 1
    where_q3 = ["1=1"]
    params_q3: dict = {}
    if filters.get("ma_nganh"):
        where_q3.append("ma_nganh = :ma_nganh")
        params_q3["ma_nganh"] = filters["ma_nganh"]
    where_q3_sql = " AND ".join(where_q3)

    q3_bands = query_records(dw_engine, f"""
        SELECT
            ten_phuong_thuc,
            CASE
                WHEN diem_quy_doi_30 < 18 THEN '1. Dưới 18'
                WHEN diem_quy_doi_30 < 21 THEN '2. 18 - <21'
                WHEN diem_quy_doi_30 < 24 THEN '3. 21 - <24'
                WHEN diem_quy_doi_30 < 27 THEN '4. 24 - <27'
                ELSE '5. Từ 27+'
            END AS nhom_diem,
            COUNT(*) AS so_sv,
            ROUND(AVG(diem_quy_doi_30), 2) AS diem_dau_vao_tb,
            ROUND(AVG(gpa_hk1_he_10), 2)   AS gpa_hk1_tb
        FROM vw_olap_tuong_quan_dau_vao_hk1
        WHERE {where_q3_sql}
        GROUP BY ten_phuong_thuc, nhom_diem
        ORDER BY ten_phuong_thuc, nhom_diem
    """, params_q3)

    q3_scatter = query_records(dw_engine, f"""
        SELECT
            ma_sv, ho_ten, ten_nganh, ma_ptxt, ten_phuong_thuc,
            diem_quy_doi_30, gpa_hk1_he_10, gpa_hk1_he_4
        FROM vw_olap_tuong_quan_dau_vao_hk1
        WHERE {where_q3_sql}
        ORDER BY ma_sv
        LIMIT 450
    """, params_q3)

    # 7. Q4: Xu hướng tuyển sinh & nhập học qua các năm theo ngành
    q4_trend = query_records(dw_engine, """
        SELECT
            ng.ma_nganh,
            ng.ten_nganh,
            tg.nam AS nam_tuyen_sinh,
            COUNT(ts.tuyen_sinh_id) AS so_ho_so,
            SUM(ts.is_trung_tuyen)  AS so_trung_tuyen,
            SUM(ts.is_nhap_hoc)     AS so_nhap_hoc,
            ROUND(AVG(ts.diem_quy_doi_30), 2) AS diem_tb_30
        FROM fact_tuyen_sinh ts
        INNER JOIN dim_nganh     ng ON ts.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON ts.thoi_gian_key = tg.thoi_gian_key
        GROUP BY ng.ma_nganh, ng.ten_nganh, tg.nam
        ORDER BY ng.ten_nganh, tg.nam
    """)

    # 8. Q5: Kết quả học tập theo Tỉnh/Thành
    q5_tinh = query_records(dw_engine, f"""
        SELECT
            sv.vung_mien,
            sv.tinh_thanh,
            COUNT(DISTINCT sv.ma_sv)                    AS so_sinh_vien,
            COUNT(kq.ket_qua_id)                        AS so_luot_hoc_phan,
            ROUND(AVG(kq.diem_tong_ket), 2)             AS diem_tb_he_10,
            ROUND(AVG(kq.diem_he_4), 2)                 AS diem_tb_he_4,
            ROUND(100.0 * AVG(kq.ket_qua_dat), 2)       AS ty_le_dat_pct,
            ROUND(100.0 * AVG(CASE WHEN kq.diem_tong_ket >= 8.0 THEN 1 ELSE 0 END), 2) AS ty_le_gioi_pct
        FROM fact_ket_qua_hoc_tap kq
        INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
        INNER JOIN dim_nganh     ng ON kq.nganh_key     = ng.nganh_key
        INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
        WHERE {where_sql}
        GROUP BY sv.vung_mien, sv.tinh_thanh
        ORDER BY diem_tb_he_10 DESC
    """, params)

    return {
        "kpi": kpi,
        "q1_khoa": q1_khoa,
        "q1_top_mon": q1_top_mon,
        "q1_hocky": q1_hocky,
        "q2_dice": q2_dice,
        "q3_bands": q3_bands,
        "q3_scatter": q3_scatter,
        "q4_trend": q4_trend,
        "q5_tinh": q5_tinh,
    }

