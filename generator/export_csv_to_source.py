import pandas as pd
import os

df_khoa = pd.read_csv('data/Khoa.csv')
df_nganh = pd.read_csv('data/Nganh.csv')
df_gv = pd.read_csv('data/GiangVien.csv')
df_mon = pd.read_csv('data/MonHoc.csv')
df_sv = pd.read_csv('data/SinhVien.csv')

lines = []
lines.append("USE edu_source;")
lines.append("GO\n")

# 1. Khoa
lines.append("-- 1. KHOA (4 rows)")
for _, r in df_khoa.iterrows():
    mk = r['ma_khoa']
    tk = str(r['ten_khoa']).replace("'", "''")
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM Khoa WHERE ma_khoa = '{mk}') INSERT INTO Khoa (ma_khoa, ten_khoa) VALUES ('{mk}', N'{tk}');")
lines.append("GO\n")

# 2. Nganh
lines.append("-- 2. NGANH (10 rows)")
for _, r in df_nganh.iterrows():
    mn = r['ma_nganh']
    tn = str(r['ten_nganh']).replace("'", "''")
    mk = r['ma_khoa']
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM Nganh WHERE ma_nganh = '{mn}') INSERT INTO Nganh (ma_nganh, ten_nganh, ma_khoa) VALUES ('{mn}', N'{tn}', '{mk}');")
lines.append("GO\n")

# 3. GiangVien (118 rows)
lines.append("-- 3. GIANGVIEN (118 rows)")
for _, r in df_gv.iterrows():
    mgv = r['ma_gv']
    ht = str(r['ho_ten']).replace("'", "''")
    hv = str(r['hoc_vi']).replace("'", "''")
    mk = r['ma_khoa']
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM GiangVien WHERE ma_gv = '{mgv}') INSERT INTO GiangVien (ma_gv, ho_ten, hoc_vi, ma_khoa) VALUES ('{mgv}', N'{ht}', N'{hv}', '{mk}');")
lines.append("GO\n")

# 4. MonHoc (120 rows)
lines.append("-- 4. MONHOC (120 rows)")
for _, r in df_mon.iterrows():
    mm = r['ma_mon']
    tm = str(r['ten_mon']).replace("'", "''")
    stc = int(r['so_tin_chi'])
    lm = str(r['loai_mon']).replace("'", "''")
    mk = r['ma_khoa']
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM MonHoc WHERE ma_mon = '{mm}') INSERT INTO MonHoc (ma_mon, ten_mon, so_tin_chi, loai_mon, ma_khoa) VALUES ('{mm}', N'{tm}', {stc}, N'{lm}', '{mk}');")
lines.append("GO\n")

# 5. SinhVien (4948 rows)
lines.append("-- 5. SINHVIEN (4948 rows)")
values = []
for i, r in df_sv.iterrows():
    msv = r['ma_sv']
    ht = str(r['ho_ten']).replace("'", "''")
    gt = str(r['gioi_tinh']) if pd.notna(r['gioi_tinh']) else 'Nam'
    ns = str(r['ngay_sinh']) if pd.notna(r['ngay_sinh']) else '2001-01-01'
    tt = str(r['tinh_thanh']).replace("'", "''") if pd.notna(r['tinh_thanh']) else 'Đà Nẵng'
    mn = str(r['ma_nganh']) if pd.notna(r['ma_nganh']) else 'IT'
    ml = str(r['ma_lop']) if pd.notna(r['ma_lop']) else '19IT1'
    values.append(f"('{msv}', N'{ht}', N'{gt}', '{ns}', N'{tt}', '{mn}', '{ml}')")
    if len(values) >= 500:
        val_str = ",\n".join(values)
        lines.append(f"INSERT INTO SinhVien (ma_sv, ho_ten, gioi_tinh, ngay_sinh, tinh_thanh, ma_nganh, ma_lop)\nSELECT v.ma_sv, v.ho_ten, v.gioi_tinh, v.ngay_sinh, v.tinh_thanh, v.ma_nganh, v.ma_lop FROM (VALUES\n{val_str}\n) AS v(ma_sv, ho_ten, gioi_tinh, ngay_sinh, tinh_thanh, ma_nganh, ma_lop) WHERE NOT EXISTS (SELECT 1 FROM SinhVien WHERE ma_sv = v.ma_sv);\nGO\n")
        values = []

if values:
    val_str = ",\n".join(values)
    lines.append(f"INSERT INTO SinhVien (ma_sv, ho_ten, gioi_tinh, ngay_sinh, tinh_thanh, ma_nganh, ma_lop)\nSELECT v.ma_sv, v.ho_ten, v.gioi_tinh, v.ngay_sinh, v.tinh_thanh, v.ma_nganh, v.ma_lop FROM (VALUES\n{val_str}\n) AS v(ma_sv, ho_ten, gioi_tinh, ngay_sinh, tinh_thanh, ma_nganh, ma_lop) WHERE NOT EXISTS (SELECT 1 FROM SinhVien WHERE ma_sv = v.ma_sv);\nGO\n")

out_path = os.path.join('sql', 'nap_du_lieu_tu_csv_sang_edu_source.sql')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"Đã tạo file {out_path} thành công!")

