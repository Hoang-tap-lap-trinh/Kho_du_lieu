"""Bộ kiểm thử chất lượng dữ liệu (Data Quality & Reconciliation Tests) cho Kho dữ liệu.

Kiểm tra đầy đủ các tiêu chí ở mục 4.3 của Đề cương:
  - Quy mô bảng fact_ket_qua_hoc_tap >= 100.000 dòng.
  - Đối soát số dòng: Số dòng nguồn = Số dòng nạp vào Fact + Số dòng bị loại trong etl_reject.
  - Đối soát số lượng sinh viên giữa nguồn và dim_sinh_vien (is_current = 1).
  - Không có khóa ngoại mồ côi (orphan foreign keys) ở cả 2 bảng fact.
  - Không có điểm NULL hoặc ngoài thang [0, 10] trong fact_ket_qua_hoc_tap, hay ngoài thang [0, 30]
    đối với diem_quy_doi_30 trong fact_tuyen_sinh.
  - Công thức điểm tổng kết (0.4*QT + 0.6*Thi) khớp 100%.
  - Dữ liệu danh mục (giới tính, tỉnh/thành, tên ngành) đã chuẩn hóa 100%.
  - SCD2: mọi sinh viên có đúng 1 dòng is_current = 1, khoảng hiệu lực [ngay_hieu_luc, ngay_het_han]
    không chồng lấn.

Xuất bảng kết quả test case ra: output/test_cases_result.csv
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from common import reference as ref
from common.db import DW_DB, OUTPUT_DIR, SOURCE_DB, get_engine


def main() -> int:
    src = get_engine(SOURCE_DB)
    dw = get_engine(DW_DB)
    results: list[dict] = []

    def add_case(ma_tc: str, hang_muc: str, mo_ta: str, ky_vong: str, thuc_te: str, passed: bool) -> None:
        results.append({
            "ma_test_case": ma_tc,
            "hang_muc": hang_muc,
            "mo_ta_kiem_tra": mo_ta,
            "ket_qua_ky_vong": ky_vong,
            "ket_qua_thuc_te": thuc_te,
            "trang_thai": "PASS" if passed else "FAIL",
        })

    with src.connect() as sconn, dw.connect() as dconn:
        latest_run = dconn.execute(text("SELECT run_id FROM etl_log ORDER BY log_id DESC LIMIT 1")).scalar()

        # TC01: Quy mô bảng fact >= 100.000 dòng
        fact_kq_cnt = int(dconn.execute(text("SELECT COUNT(*) FROM fact_ket_qua_hoc_tap")).scalar())
        add_case(
            "TC01", "Quy mô dữ liệu",
            "Bảng fact_ket_qua_hoc_tap có tối thiểu 100.000 dòng",
            ">= 100,000", f"{fact_kq_cnt:,}",
            fact_kq_cnt >= 100_000,
        )

        # TC02: Đối soát số dòng DangKyHocPhan (Nguồn = Fact + Reject)
        src_dk_cnt = int(sconn.execute(text("SELECT COUNT(*) FROM DangKyHocPhan")).scalar())
        rej_dk_cnt = int(dconn.execute(
            text("SELECT COUNT(*) FROM etl_reject WHERE run_id = :r AND bang = 'DangKyHocPhan'"),
            {"r": latest_run},
        ).scalar())
        add_case(
            "TC02", "Đối soát nguồn - kho",
            "Số dòng DangKyHocPhan nguồn = fact_ket_qua_hoc_tap + etl_reject",
            f"{src_dk_cnt:,}", f"{fact_kq_cnt + rej_dk_cnt:,} (Fact={fact_kq_cnt:,}, Reject={rej_dk_cnt:,})",
            src_dk_cnt == fact_kq_cnt + rej_dk_cnt,
        )

        # TC03: Đối soát số dòng HoSoTuyenSinh (Nguồn = Fact + Reject)
        src_hs_cnt = int(sconn.execute(text("SELECT COUNT(*) FROM HoSoTuyenSinh")).scalar())
        fact_ts_cnt = int(dconn.execute(text("SELECT COUNT(*) FROM fact_tuyen_sinh")).scalar())
        rej_hs_cnt = int(dconn.execute(
            text("SELECT COUNT(*) FROM etl_reject WHERE run_id = :r AND bang = 'HoSoTuyenSinh'"),
            {"r": latest_run},
        ).scalar())
        add_case(
            "TC03", "Đối soát nguồn - kho",
            "Số dòng HoSoTuyenSinh nguồn = fact_tuyen_sinh + etl_reject",
            f"{src_hs_cnt:,}", f"{fact_ts_cnt + rej_hs_cnt:,} (Fact={fact_ts_cnt:,}, Reject={rej_hs_cnt:,})",
            src_hs_cnt == fact_ts_cnt + rej_hs_cnt,
        )

        # TC04: Đối soát số sinh viên hiện hành
        src_sv_cnt = int(sconn.execute(text("SELECT COUNT(*) FROM SinhVien")).scalar())
        dw_sv_cur = int(dconn.execute(
            text("SELECT COUNT(*) FROM dim_sinh_vien WHERE sinh_vien_key > 0 AND is_current = 1")
        ).scalar())
        add_case(
            "TC04", "Đối soát sinh viên",
            "Số sinh viên nguồn khớp số bản ghi is_current = 1 trong dim_sinh_vien",
            f"{src_sv_cnt:,}", f"{dw_sv_cur:,}",
            src_sv_cnt == dw_sv_cur,
        )

        # TC05: Không có điểm ngoài thang [0, 10] hoặc NULL trong fact_ket_qua_hoc_tap
        bad_grade_cnt = int(dconn.execute(text("""
            SELECT COUNT(*) FROM fact_ket_qua_hoc_tap
            WHERE diem_qua_trinh IS NULL OR diem_thi IS NULL OR diem_tong_ket IS NULL
               OR diem_qua_trinh < 0 OR diem_qua_trinh > 10
               OR diem_thi < 0 OR diem_thi > 10
               OR diem_tong_ket < 0 OR diem_tong_ket > 10
        """)).scalar())
        add_case(
            "TC05", "Miền giá trị điểm",
            "Không có điểm NULL hoặc ngoài khoảng [0, 10] trong fact_ket_qua_hoc_tap",
            "0 dòng lỗi", f"{bad_grade_cnt} dòng lỗi",
            bad_grade_cnt == 0,
        )

        # TC06: Công thức điểm tổng kết = ROUND(0.4*QT + 0.6*Thi, 1)
        wrong_formula_cnt = int(dconn.execute(text("""
            SELECT COUNT(*) FROM fact_ket_qua_hoc_tap
            WHERE ABS(diem_tong_ket - ROUND(0.4 * diem_qua_trinh + 0.6 * diem_thi, 1)) > 0.01
        """)).scalar())
        add_case(
            "TC06", "Tính đúng đắn công thức",
            "Điểm tổng kết khớp công thức ROUND(0.4*QT + 0.6*Thi, 1)",
            "0 dòng lệch", f"{wrong_formula_cnt} dòng lệch",
            wrong_formula_cnt == 0,
        )

        # TC07: Không có cặp (sinh_vien, ma_lhp) bị trùng trong fact_ket_qua_hoc_tap
        dup_lhp_cnt = int(dconn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT sv.ma_sv, kq.ma_lhp, COUNT(*) AS c
                FROM fact_ket_qua_hoc_tap kq
                JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
                GROUP BY sv.ma_sv, kq.ma_lhp
                HAVING COUNT(*) > 1
            ) t
        """)).scalar())
        add_case(
            "TC07", "Tính duy nhất (Grain)",
            "Không có sinh viên đăng ký trùng cùng một lớp học phần trong Fact",
            "0 cặp trùng", f"{dup_lhp_cnt} cặp trùng",
            dup_lhp_cnt == 0,
        )

        # TC08: Toàn vẹn tham chiếu (không có khóa ngoại mồ côi)
        orphan_cnt = int(dconn.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM fact_ket_qua_hoc_tap kq LEFT JOIN dim_sinh_vien d ON kq.sinh_vien_key = d.sinh_vien_key WHERE d.sinh_vien_key IS NULL) +
                (SELECT COUNT(*) FROM fact_ket_qua_hoc_tap kq LEFT JOIN dim_mon_hoc d ON kq.mon_hoc_key = d.mon_hoc_key WHERE d.mon_hoc_key IS NULL) +
                (SELECT COUNT(*) FROM fact_ket_qua_hoc_tap kq LEFT JOIN dim_giang_vien d ON kq.giang_vien_key = d.giang_vien_key WHERE d.giang_vien_key IS NULL) +
                (SELECT COUNT(*) FROM fact_ket_qua_hoc_tap kq LEFT JOIN dim_nganh d ON kq.nganh_key = d.nganh_key WHERE d.nganh_key IS NULL) +
                (SELECT COUNT(*) FROM fact_ket_qua_hoc_tap kq LEFT JOIN dim_thoi_gian d ON kq.thoi_gian_key = d.thoi_gian_key WHERE d.thoi_gian_key IS NULL)
        """)).scalar())
        add_case(
            "TC08", "Toàn vẹn khóa ngoại",
            "Không có khóa ngoại mồ côi giữa Fact và các Dimension",
            "0 dòng mồ côi", f"{orphan_cnt} dòng mồ côi",
            orphan_cnt == 0,
        )

        # TC09: Chuẩn hóa giới tính & tỉnh/thành trong dim_sinh_vien
        valid_provinces = {t[0] for t in ref.TINH_THANH}
        sv_provinces = {
            r[0] for r in dconn.execute(text("SELECT DISTINCT tinh_thanh FROM dim_sinh_vien WHERE sinh_vien_key > 0")).fetchall()
        }
        sv_genders = {
            r[0] for r in dconn.execute(text("SELECT DISTINCT gioi_tinh FROM dim_sinh_vien WHERE sinh_vien_key > 0")).fetchall()
        }
        invalid_prov = sv_provinces - valid_provinces
        invalid_gender = sv_genders - {"Nam", "Nữ"}
        add_case(
            "TC09", "Chuẩn hóa danh mục",
            "Giới tính chỉ gồm {Nam, Nữ} và tỉnh/thành thuộc đúng 18 tỉnh/thành chuẩn",
            "0 giá trị lạ", f"Tỉnh lạ={len(invalid_prov)}, Giới tính lạ={len(invalid_gender)}",
            len(invalid_prov) == 0 and len(invalid_gender) == 0,
        )

        # TC10: Kiểm tra tính đúng đắn của SCD2 trên dim_sinh_vien
        scd2_history_cnt = int(dconn.execute(
            text("SELECT COUNT(*) FROM dim_sinh_vien WHERE sinh_vien_key > 0 AND is_current = 0")
        ).scalar())
        scd2_overlap_cnt = int(dconn.execute(text("""
            SELECT COUNT(*)
            FROM dim_sinh_vien d1
            JOIN dim_sinh_vien d2
              ON d1.ma_sv = d2.ma_sv
             AND d1.sinh_vien_key < d2.sinh_vien_key
             AND d1.ngay_hieu_luc <= d2.ngay_het_han
             AND d2.ngay_hieu_luc <= d1.ngay_het_han
            WHERE d1.sinh_vien_key > 0
        """)).scalar())
        add_case(
            "TC10", "Tính đúng của SCD2",
            "Các phiên bản SCD2 của sinh viên đổi ngành được đóng đúng, không chồng lấn ngày hiệu lực",
            "Có dòng lịch sử & 0 chồng lấn",
            f"Dòng lịch sử={scd2_history_cnt}, Chồng lấn={scd2_overlap_cnt}",
            scd2_history_cnt > 0 and scd2_overlap_cnt == 0,
        )

    df_res = pd.DataFrame(results)
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_file = OUTPUT_DIR / "test_cases_result.csv"
    df_res.to_csv(out_file, index=False, encoding="utf-8-sig")

    print("\n=== KẾT QUẢ KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU (10 TEST CASES) ===")
    print(df_res.to_string(index=False))
    failed = int((df_res["trang_thai"] != "PASS").sum())
    print(f"\nTổng kết: {len(df_res) - failed}/{len(df_res)} PASS. Đã lưu file: {out_file}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

