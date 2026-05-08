#!/usr/bin/env python3
"""
Collect Database Training Data

Trích xuất dữ liệu phản hồi (HTTP Response) từ cơ sở dữ liệu của ứng dụng
để tạo thành file CSV phục vụ việc huấn luyện mô hình AI.
"""

import os
import sys

# Add project root to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from ai.data_collector import TrainingDataCollector

def main():
    print("[DB Collector] Khởi tạo ứng dụng Flask...")
    # Cần tạo app_context để có thể truy vấn Database bằng SQLAlchemy
    app = create_app()
    
    collector = TrainingDataCollector()
    print("[DB Collector] Đang thu thập dữ liệu từ Database (bảng vulnerabilities và pages)...")
    
    try:
        collector.collect_from_db(app)
    except Exception as e:
        print(f"[ERROR] Lỗi khi truy vấn Database: {e}")
        sys.exit(1)
        
    output_path = 'data/raw/real_training_data.csv'
    
    try:
        collector.save_to_csv(output_path)
        print(f"[DB Collector] Thu thập thành công!")
        print(f"File đã được lưu tại: {output_path}")
    except ValueError as e:
        print(f"[DB Collector] {e}")
        print("Lưu ý: Có thể Database của bạn chưa có dữ liệu nào. Hãy dùng Scanner để quét trang DVWA trước khi thu thập.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Không thể lưu file CSV: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
