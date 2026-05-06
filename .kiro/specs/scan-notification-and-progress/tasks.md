# Tasks

## Implementation Tasks

- [x] 1. Add `_get_last_scan()` helper and update GET handler in `app/routes/scan.py`
  - [x] 1.1 Thêm import `flash` vào `app/routes/scan.py`
  - [x] 1.2 Viết hàm `_get_last_scan()` query DB lấy scan gần nhất (status completed/failed, order by completed_at DESC, limit 1), bắt exception trả về None
  - [x] 1.3 Cập nhật GET handler của `new_scan()` để gọi `_get_last_scan()` và truyền `last_scan` vào `render_template`
  - [x] 1.4 Cập nhật POST handler của `new_scan()` để gọi `flash()` với category `'scan_success'` sau khi scan thành công, và `'scan_error'` khi scan thất bại

- [x] 2. Thêm Toast Notification vào `templates/base.html` và `app/static/js/main.js`
  - [x] 2.1 Thêm toast container HTML vào `base.html` (đọc flash messages bằng Jinja2 `get_flashed_messages(with_categories=True)`, render toast cho category `scan_success` và `scan_error`)
  - [x] 2.2 Thêm CSS cho `.toast-container`, `.toast`, `.toast--success`, `.toast--error`, `.toast-close` vào `app/static/css/style.css`
  - [x] 2.3 Thêm hàm `initToastNotifications()` vào `app/static/js/main.js` (gắn close button handler, setTimeout auto-dismiss 5000ms)
  - [x] 2.4 Gọi `initToastNotifications()` trong `DOMContentLoaded` listener của `main.js`

- [x] 3. Thêm Previous Scan Progress Panel vào `templates/scan.html`
  - [x] 3.1 Thêm block HTML cho Progress Panel bên dưới form trong `scan.html` (conditional render dựa trên `last_scan`, hiển thị đủ 6 trường: target_url, status, total_pages, total_forms, total_vulnerabilities, completed_at)
  - [x] 3.2 Thêm logic badge: `total_vulnerabilities > 0` → badge danger, `total_vulnerabilities == 0` → badge success, `status == 'failed'` → badge error
  - [x] 3.3 Thêm "View Full Results" link trỏ đến `url_for('results.show_results', scan_id=last_scan.id)` và "View All History" link trỏ đến `url_for('history.scan_history')`
  - [x] 3.4 Thêm CSS cho `.progress-panel`, `.panel-badge`, `.panel-badge--danger`, `.panel-badge--success`, `.panel-badge--error` vào `app/static/css/style.css`

- [x] 4. Viết unit tests và property-based tests
  - [x] 4.1 Tạo file `tests/test_scan_notification.py` với unit tests example-based (toast render, panel render, empty state, failed state, clean scan state, DB error fallback)
  - [x] 4.2 Tạo file `tests/test_scan_notification_properties.py` với property-based tests dùng Hypothesis (6 properties từ design document)
  - [x] 4.3 Chạy toàn bộ test suite `python -m pytest tests/ -v` và xác nhận không có regression
