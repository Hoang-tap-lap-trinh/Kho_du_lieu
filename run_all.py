"""Chạy trọn gói toàn bộ đồ án Kho dữ liệu giáo dục bằng 1 lệnh duy nhất.

Thứ tự thực hiện:
  1. Kiểm tra kết nối MariaDB / MySQL (theo file .env).
  2. Tạo CSDL nguồn edu_source (3NF) và sinh dữ liệu giả lập (~240.000 dòng kết quả học tập,
     ~8.000 hồ sơ tuyển sinh, có chèn lỗi chủ đích).
  3. Tạo Kho dữ liệu edu_dw (Star Schema), cài đặt Stored Procedures và chạy quy trình ETL.
  4. Chạy kịch bản minh họa SCD loại 2 (đổi ngành sinh viên ở nguồn -> ETL tạo bản ghi lịch sử;
     chạy lặp kiểm tra idempotent).
  5. Chạy 10 Test Cases kiểm thử chất lượng dữ liệu.
  6. Chạy 5 câu hỏi phân tích OLAP và đo hiệu năng (Star Schema vs OLTP 3NF).

Cách chạy:
    .venv\\Scripts\\python.exe run_all.py
"""
from __future__ import annotations

import argparse
import time
from sqlalchemy import text
from common.db import SOURCE_DB, get_engine
from common.check_connection import main as check_conn
from generator.generate_data import main as gen_data
from etl.pipeline import run_etl
from etl.demo_scd2 import main as demo_scd2
from tests.run_dq_tests import main as run_tests
from analysis.benchmark import main as run_benchmark


def _source_already_populated() -> bool:
    try:
        eng = get_engine(SOURCE_DB)
        with eng.connect() as conn:
            cnt = int(conn.execute(text("SELECT COUNT(*) FROM DangKyHocPhan")).scalar())
            return cnt >= 100_000
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Chạy trọn gói đồ án Kho dữ liệu giáo dục")
    parser.add_argument("--force-generate", action="store_true", help="Sinh và nạp lại edu_source kể cả khi đã có dữ liệu")
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 80)
    print("BƯỚC 1/6: KIỂM TRA KẾT NỐI MARIADB / MYSQL")
    print("=" * 80)
    if check_conn() != 0:
        return 1

    print("\n" + "=" * 80)
    print("BƯỚC 2/6: TẠO CSDL NGUỒN (edu_source) & SINH DỮ LIỆU GIẢ LẬP (>= 240.000 DÒNG)")
    print("=" * 80)
    if not args.force_generate and _source_already_populated():
        print("[SKIP] edu_source đã có sẵn dữ liệu (>= 100.000 dòng DangKyHocPhan). Dùng --force-generate nếu muốn tạo lại.")
    else:
        gen_data()

    print("\n" + "=" * 80)
    print("BƯỚC 3/6: TẠO KHO DỮ LIỆU (edu_dw) & CHẠY QUY TRÌNH ETL LẦN ĐẦU")
    print("=" * 80)
    run_etl(init_dw=True)

    print("\n" + "=" * 80)
    print("BƯỚC 4/6: DEMO SLOWLY CHANGING DIMENSION LOẠI 2 (SCD2) & KIỂM TRA CHẠY LẶP")
    print("=" * 80)
    demo_scd2()

    print("\n" + "=" * 80)
    print("BƯỚC 5/6: KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU (10 TEST CASES)")
    print("=" * 80)
    rc = run_tests()

    print("\n" + "=" * 80)
    print("BƯỚC 6/6: TRUY VẤN OLAP 5 CÂU HỎI QUẢN LÝ & ĐO HIỆU NĂNG")
    print("=" * 80)
    run_benchmark()

    print("\n" + "=" * 80)
    print(f"HOÀN TẤT TOÀN BỘ PIPELINE SAU {time.time() - t0:.1f} GIÂY!")
    print("Toàn bộ báo cáo CSV đã xuất vào thư mục: Code/output/")
    print("=" * 80)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

