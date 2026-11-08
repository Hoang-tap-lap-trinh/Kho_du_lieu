"""Quy tắc tính điểm dùng chung cho bộ sinh dữ liệu và ETL.

- Điểm tổng kết = 40% điểm quá trình + 60% điểm thi, làm tròn 1 chữ số thập phân
  theo kiểu "half-up" (giống hàm ROUND của MySQL trên kiểu DECIMAL).
- Quy đổi điểm chữ / thang 4 theo quy chế đào tạo tín chỉ phổ biến ở Việt Nam.
"""
from __future__ import annotations

import numpy as np

TRONG_SO_QUA_TRINH = 0.4
TRONG_SO_THI = 0.6
DIEM_DAT = 4.0

# (ngưỡng dưới, điểm chữ, điểm hệ 4) - xét từ trên xuống
BANG_QUY_DOI = [
    (8.5, "A", 4.0),
    (8.0, "B+", 3.5),
    (7.0, "B", 3.0),
    (6.5, "C+", 2.5),
    (5.5, "C", 2.0),
    (5.0, "D+", 1.5),
    (4.0, "D", 1.0),
    (0.0, "F", 0.0),
]


def round_half_up(values, decimals: int = 1):
    """Làm tròn half-up (7.25 -> 7.3), tránh kiểu banker's rounding của numpy."""
    factor = 10 ** decimals
    arr = np.asarray(values, dtype=float)
    return np.floor(arr * factor + 0.5 + 1e-9) / factor


def tinh_diem_tong_ket(diem_qua_trinh, diem_thi):
    return round_half_up(
        TRONG_SO_QUA_TRINH * np.asarray(diem_qua_trinh, dtype=float)
        + TRONG_SO_THI * np.asarray(diem_thi, dtype=float),
        1,
    )


def quy_doi_diem(diem_tong_ket):
    """Trả về (mảng điểm chữ, mảng điểm hệ 4) cho mảng điểm tổng kết thang 10."""
    tk = np.asarray(diem_tong_ket, dtype=float)
    conditions = [tk >= nguong for nguong, _, _ in BANG_QUY_DOI]
    diem_chu = np.select(conditions, [c for _, c, _ in BANG_QUY_DOI], default="F")
    diem_he_4 = np.select(conditions, [h for _, _, h in BANG_QUY_DOI], default=0.0)
    return diem_chu, diem_he_4

