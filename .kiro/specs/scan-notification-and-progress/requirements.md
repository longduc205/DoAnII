# Requirements Document

## Introduction

Tính năng này bổ sung hai cải tiến UX cho trang **New Scan** của ứng dụng AI Web Vulnerability Scanner:

1. **Scan Completion Notification** — Hiển thị thông báo (toast/banner) ngay khi quá trình scan một URL hoàn tất, giúp người dùng nhận biết kết quả mà không cần theo dõi liên tục.
2. **Previous Scan Progress Panel** — Hiển thị thông tin tóm tắt của lần scan gần nhất ngay bên dưới form New Scan, cho phép người dùng xem lại kết quả vừa thực hiện mà không cần chuyển sang trang History hay Results.

Cả hai tính năng đều hoạt động hoàn toàn phía client (JavaScript + Jinja2 template), tận dụng dữ liệu scan đã có trong database thông qua Flask route hiện tại, không yêu cầu thay đổi schema database.

---

## Glossary

- **Notification_System**: Thành phần frontend hiển thị thông báo dạng toast/banner sau khi scan hoàn tất.
- **Progress_Panel**: Thành phần UI hiển thị tóm tắt kết quả của lần scan gần nhất bên dưới form New Scan.
- **Scan_Summary**: Tập hợp thông tin tóm tắt của một scan session bao gồm: target URL, trạng thái, số trang, số form, số lỗ hổng, thời gian hoàn tất.
- **Last_Scan**: Scan session có `completed_at` mới nhất trong database, bất kể người dùng nào thực hiện (single-user academic context).
- **Toast**: Thông báo nhỏ xuất hiện tạm thời ở góc màn hình, tự động biến mất sau một khoảng thời gian.
- **Scan_Page**: Trang `/scan/new` trong ứng dụng Flask.
- **Scanner_Engine**: Service `app/services/scanner.py` điều phối toàn bộ pipeline scan.
- **Scan_Route**: Flask route handler tại `app/routes/scan.py`.

---

## Requirements

### Requirement 1: Scan Completion Notification

**User Story:** As a user, I want to see a notification when my scan finishes, so that I know the scan is complete without having to watch the progress screen continuously.

#### Acceptance Criteria

1. WHEN a scan completes successfully, THE Notification_System SHALL display a toast notification containing the target URL and total vulnerabilities found.
2. WHEN a scan fails with an error, THE Notification_System SHALL display a toast notification indicating the scan failed with a brief error description.
3. THE Notification_System SHALL display the success toast with a green visual indicator and the failure toast with a red visual indicator to distinguish outcomes.
4. WHEN a toast notification is displayed, THE Notification_System SHALL automatically dismiss it after 5 seconds.
5. WHEN a toast notification is displayed, THE Notification_System SHALL provide a manual close button so the user can dismiss it before the 5-second timeout.
6. THE Notification_System SHALL display the toast notification in the top-right corner of the viewport, above all other page content.
7. WHEN the scan completes and the results page loads, THE Notification_System SHALL display the toast notification on the results page immediately after redirect.

### Requirement 2: Previous Scan Progress Panel

**User Story:** As a user, I want to see a summary of my most recent scan directly on the New Scan page, so that I can review the last result without navigating away.

#### Acceptance Criteria

1. WHEN the Scan_Page loads and a completed scan exists in the database, THE Progress_Panel SHALL display the Scan_Summary of the Last_Scan below the scan configuration form.
2. WHEN the Scan_Page loads and no completed scan exists in the database, THE Progress_Panel SHALL display a placeholder message indicating no previous scans are available.
3. THE Progress_Panel SHALL display the following fields from the Last_Scan: target URL, scan status, total pages crawled, total forms found, total vulnerabilities detected, and completion timestamp.
4. WHEN the Last_Scan has `status = 'completed'` and `total_vulnerabilities > 0`, THE Progress_Panel SHALL display a visual severity indicator (e.g., colored badge) alongside the vulnerability count.
5. WHEN the Last_Scan has `status = 'completed'` and `total_vulnerabilities = 0`, THE Progress_Panel SHALL display a "No vulnerabilities found" indicator with a green visual style.
6. WHEN the Last_Scan has `status = 'failed'`, THE Progress_Panel SHALL display a "Scan failed" indicator with a red visual style.
7. THE Progress_Panel SHALL include a "View Full Results" link that navigates to the results page for the Last_Scan.
8. THE Progress_Panel SHALL include a "View All History" link that navigates to the scan history page.
9. WHEN a new scan is submitted from the Scan_Page, THE Scan_Route SHALL pass the Last_Scan data to the `scan.html` template so the Progress_Panel renders on page load.

### Requirement 3: Data Access for Last Scan

**User Story:** As a developer, I want the New Scan page to efficiently retrieve the last scan summary, so that the page loads quickly without impacting scan performance.

#### Acceptance Criteria

1. THE Scan_Route SHALL query the database for the single most recent Scan record with `status IN ('completed', 'failed')` ordered by `completed_at DESC` with `LIMIT 1`.
2. WHEN the Scan_Route handles a GET request to `/scan/new`, THE Scan_Route SHALL pass the Last_Scan object (or `None`) to the `scan.html` template as a template variable named `last_scan`.
3. THE Scan_Route SHALL retrieve the Last_Scan data using a single database query to avoid N+1 query issues.
4. IF the database query for Last_Scan raises an exception, THEN THE Scan_Route SHALL log the error and pass `None` as `last_scan` so the page still renders without the Progress_Panel data.

### Requirement 4: Notification Persistence Across Redirect

**User Story:** As a user, I want the scan completion notification to appear on the results page after the redirect, so that I see the notification even though the page has changed.

#### Acceptance Criteria

1. WHEN a scan completes and the server redirects to the results page, THE Scan_Route SHALL store a flash message containing the scan outcome (success or failure) using Flask's flash mechanism.
2. WHEN the results page renders and a flash message is present, THE Notification_System SHALL read the flash message and display the corresponding toast notification.
3. THE Notification_System SHALL support two flash message categories: `'scan_success'` for completed scans and `'scan_error'` for failed scans.
4. WHEN a flash message of category `'scan_success'` is present, THE Notification_System SHALL display the success toast with vulnerability count extracted from the flash message payload.
5. IF no flash message is present on the results page, THEN THE Notification_System SHALL display no toast notification.
