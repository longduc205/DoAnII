#!/usr/bin/env python3
"""
Merge Datasets Script

Gộp dữ liệu giả lập (synthetic) và dữ liệu thực tế (từ DB/DVWA)
thành một tập dữ liệu lai (Hybrid Dataset) duy nhất phục vụ huấn luyện AI.
"""

import os
import sys
import pandas as pd

def main():
    # Đường dẫn file
    synthetic_file = 'data/raw/training_data.csv'
    real_file = 'data/raw/real_training_data.csv'
    output_file = 'data/raw/combined_training_data.csv'

    print("=== HYBRID DATASET MERGER ===")

    # Kiểm tra file giả lập
    if not os.path.exists(synthetic_file):
        print(f"[LỖI] Không tìm thấy {synthetic_file}")
        print("Vui lòng chạy lệnh: python scripts/generate_training_data.py trước!")
        sys.exit(1)

    df_synthetic = pd.read_csv(synthetic_file)
    print(f"[*] Đã tải dữ liệu giả lập: {len(df_synthetic)} mẫu.")

    # Kiểm tra file thực tế
    if not os.path.exists(real_file):
        print(f"[CẢNH BÁO] Không tìm thấy {real_file}")
        print("Vui lòng quét DVWA và chạy: python scripts/collect_db_data.py")
        print("Tạm thời bỏ qua việc gộp dữ liệu thực tế...\n")
        df_real = pd.DataFrame()
    else:
        df_real = pd.read_csv(real_file)
        print(f"[*] Đã tải dữ liệu thực tế (DVWA): {len(df_real)} mẫu.")

    # Gộp 2 dataframe
    if not df_real.empty:
        df_combined = pd.concat([df_synthetic, df_real], ignore_index=True)
        # Xáo trộn dữ liệu (shuffle) để AI học tốt hơn
        df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    else:
        df_combined = df_synthetic

    # Lưu ra file mới
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_combined.to_csv(output_file, index=False)

    print(f"\n[THÀNH CÔNG] Đã lưu dữ liệu lai vào: {output_file}")
    print(f"Tổng số mẫu dữ liệu: {len(df_combined)}")
    
    # Thống kê nhanh các nhãn
    if 'label' in df_combined.columns:
        counts = df_combined['label'].value_counts()
        print(f"  - Bình thường (0): {counts.get(0, 0)} mẫu")
        print(f"  - Đáng ngờ (1) : {counts.get(1, 0)} mẫu")

    print("\n[HƯỚNG DẪN TIẾP THEO]")
    print("Bạn có thể mở file ai/trainer.py và thay đổi đường dẫn file dữ liệu")
    print(f"từ 'data/raw/training_data.csv' thành '{output_file}' để huấn luyện AI.")

if __name__ == '__main__':
    main()
