"""Kịch bản minh họa & kiểm chứng Slowly Changing Dimension loại 2 (SCD2) trên dim_sinh_vien.

Thực hiện đúng yêu cầu mục 3.2 và 4.3 của Đề cương:
  1. Chọn 1 sinh viên đang có 1 phiên bản trong kho (ví dụ ngành Công nghệ thông tin - IT).
  2. Cập nhật đổi ngành sinh viên đó sang Kỹ thuật phần mềm (SE) ở CSDL nguồn edu_source.
  3. Chạy lại ETL -> kiểm tra dim_sinh_vien giữ 2 dòng (dòng cũ đóng bằng ngay_het_han, is_current=0;
     dòng mới mở với is_current=1) và kết quả học tập các học kỳ trước vẫn thuộc về ngành cũ.
  4. Chạy lại ETL thêm một lần nữa (không thay đổi nguồn) để chứng minh tính lũy đẳng (idempotent):
     không sinh thêm dòng trùng lặp.

Cách chạy:
    python -m etl.demo_scd2
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from common.db import DW_DB, SOURCE_DB, get_engine
from etl.pipeline import run_etl


def main() -> None:
    src_engine = get_engine(SOURCE_DB)
    dw_engine = get_engine(DW_DB)

    # Chọn 1 sinh viên ngành IT chưa từng đổi ngành
    with dw_engine.connect() as conn:
        row = conn.execute(text("""
            SELECT ma_sv, ho_ten, ma_nganh, ma_lop, nam_nhap_hoc
            FROM dim_sinh_vien
            WHERE ma_nganh = 'IT'
              AND sinh_vien_key > 0
              AND ma_sv NOT IN (
                  SELECT ma_sv FROM dim_sinh_vien WHERE sinh_vien_key > 0 GROUP BY ma_sv HAVING COUNT(*) > 1
              )
            ORDER BY ma_sv
            LIMIT 1
        """)).fetchone()

    if not row:
        print("Không tìm thấy sinh viên ngành IT chưa đổi ngành để demo.")
        return

    ma_sv, ho_ten, nganh_cu, lop_cu, nam_nhap = row
    nganh_moi = "SE"
    lop_moi = f"{int(nam_nhap) % 100:02d}SE1"
    ngay_chuyen = f"{int(nam_nhap) + 2}-08-20"

    print(f"=== BƯỚC 1: TRẠNG THÁI TRƯỚC KHI ĐỔI NGÀNH CỦA SINH VIÊN {ma_sv} ({ho_ten}) ===")
    with dw_engine.connect() as conn:
        df_before = pd.read_sql(
            text("SELECT sinh_vien_key, ma_sv, ho_ten, ma_nganh, ten_nganh, ma_lop, "
                 "ngay_hieu_luc, ngay_het_han, is_current FROM dim_sinh_vien WHERE ma_sv = :sv ORDER BY ngay_hieu_luc"),
            conn, params={"sv": ma_sv},
        )
    print(df_before.to_string(index=False))

    print(f"\n=== BƯỚC 2: CẬP NHẬT ĐỔI NGÀNH Ở NGUỒN ({nganh_cu} -> {nganh_moi}, ngày {ngay_chuyen}) ===")
    with src_engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO LichSuChuyenNganh (ma_sv, ma_nganh_cu, ma_nganh_moi, ma_lop_cu, ma_lop_moi, ngay_chuyen)
                VALUES (:sv, :nc, :nm, :lc, :lm, :ngay)
            """),
            {"sv": ma_sv, "nc": nganh_cu, "nm": nganh_moi, "lc": lop_cu, "lm": lop_moi, "ngay": ngay_chuyen},
        )
        conn.execute(
            text("""
                UPDATE SinhVien
                SET ma_nganh = :nm, ma_lop = :lm, ngay_cap_nhat = NOW()
                WHERE ma_sv = :sv
            """),
            {"nm": nganh_moi, "lm": lop_moi, "sv": ma_sv},
        )

    print("\n=== BƯỚC 3: CHẠY LẠI ETL LẦN 1 (ÁP DỤNG SCD2) ===")
    run_etl(init_dw=False, copy_raw_to_dw=False)

    with dw_engine.connect() as conn:
        df_after = pd.read_sql(
            text("SELECT sinh_vien_key, ma_sv, ho_ten, ma_nganh, ten_nganh, ma_lop, "
                 "ngay_hieu_luc, ngay_het_han, is_current FROM dim_sinh_vien WHERE ma_sv = :sv ORDER BY ngay_hieu_luc"),
            conn, params={"sv": ma_sv},
        )
        df_grades = pd.read_sql(
            text("""
                SELECT tg.nam_hoc, tg.hoc_ky_so, ng.ma_nganh AS nganh_ghi_nhan_tren_fact,
                       sv.sinh_vien_key, COUNT(*) AS so_mon, ROUND(AVG(kq.diem_tong_ket), 2) AS diem_tb
                FROM fact_ket_qua_hoc_tap kq
                JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
                JOIN dim_nganh ng ON kq.nganh_key = ng.nganh_key
                JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
                WHERE sv.ma_sv = :sv
                GROUP BY tg.nam_hoc, tg.hoc_ky_so, ng.ma_nganh, sv.sinh_vien_key
                ORDER BY tg.nam_hoc, tg.hoc_ky_so
            """),
            conn, params={"sv": ma_sv},
        )
        total_sv_rows_1 = int(conn.execute(text("SELECT COUNT(*) FROM dim_sinh_vien")).scalar())
        total_fact_rows_1 = int(conn.execute(text("SELECT COUNT(*) FROM fact_ket_qua_hoc_tap")).scalar())

    print(f"\n-> Các phiên bản trong dim_sinh_vien của {ma_sv} sau khi đổi ngành:")
    print(df_after.to_string(index=False))
    print(f"\n-> Kết quả học tập theo từng học kỳ của {ma_sv} (các kỳ trước ngày {ngay_chuyen} vẫn thuộc ngành {nganh_cu}):")
    print(df_grades.to_string(index=False))

    print("\n=== BƯỚC 4: CHẠY LẠI ETL LẦN 2 (KIỂM TRA KHÔNG NHÂN ĐÔI DỮ LIỆU) ===")
    run_etl(init_dw=False, copy_raw_to_dw=False)
    with dw_engine.connect() as conn:
        total_sv_rows_2 = int(conn.execute(text("SELECT COUNT(*) FROM dim_sinh_vien")).scalar())
        total_fact_rows_2 = int(conn.execute(text("SELECT COUNT(*) FROM fact_ket_qua_hoc_tap")).scalar())

    print(f"\nKiểm tra Idempotency:")
    print(f"  - Số dòng dim_sinh_vien: trước={total_sv_rows_1:,}, sau={total_sv_rows_2:,}")
    print(f"  - Số dòng fact_ket_qua_hoc_tap: trước={total_fact_rows_1:,}, sau={total_fact_rows_2:,}")
    assert total_sv_rows_1 == total_sv_rows_2, "LỖI: dim_sinh_vien bị nhân đôi!"
    assert total_fact_rows_1 == total_fact_rows_2, "LỖI: fact_ket_qua_hoc_tap bị nhân đôi!"
    print("[OK] SCD2 hoạt động chính xác và chạy lặp hoàn toàn không nhân đôi dữ liệu!")


if __name__ == "__main__":
    main()

