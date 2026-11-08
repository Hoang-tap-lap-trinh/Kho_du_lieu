"""Kiểm tra kết nối tới MariaDB / MySQL theo cấu hình trong file .env."""
from __future__ import annotations

import sys
from sqlalchemy import text
from common.db import DB_HOST, DB_PORT, DB_USER, SOURCE_DB, DW_DB, get_engine


def main() -> int:
    print(f"Đang kiểm tra kết nối tới {DB_USER}@{DB_HOST}:{DB_PORT} ...")
    try:
        engine = get_engine()
        with engine.connect() as conn:
            ver = conn.execute(text("SELECT VERSION()")).scalar()
            print(f"[OK] Kết nối thành công! Phiên bản CSDL: {ver}")
            dbs = [r[0] for r in conn.execute(text("SHOW DATABASES")).fetchall()]
            print(f"     - {SOURCE_DB}: {'ĐÃ CÓ' if SOURCE_DB in dbs else 'chưa tạo'}")
            print(f"     - {DW_DB}: {'ĐÃ CÓ' if DW_DB in dbs else 'chưa tạo'}")
        return 0
    except Exception as exc:
        print(f"[LỖI] Không kết nối được CSDL với mật khẩu trong .env: {exc}", file=sys.stderr)
        # Thử kiểm tra xem MariaDB XAMPP có đang để mật khẩu rỗng mặc định không
        try:
            import pymysql
            c = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password="")
            ver = c.get_server_info()
            c.close()
            print(f"[GỢI Ý] MariaDB ({ver}) trên máy bạn hiện đang KHÔNG đặt mật khẩu (mật khẩu rỗng mặc định của XAMPP).", file=sys.stderr)
            print("-> Hãy để trống dòng DB_PASSWORD= trong file Code/.env", file=sys.stderr)
        except Exception as exc2:
            print(f"[CHI TIẾT] Thử mật khẩu rỗng cũng báo: {exc2}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

