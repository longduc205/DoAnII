# CHƯƠNG 5: KIỂM THỬ VÀ ĐÁNH GIÁ

Chương này trình bày toàn bộ quá trình kiểm thử và đánh giá hệ thống quét lỗ hổng web tích hợp trí tuệ nhân tạo đã được thiết kế và triển khai ở các chương trước. Nội dung bao gồm mô tả chi tiết môi trường kiểm thử, các kịch bản kiểm thử chức năng cho từng module thành phần, đánh giá hiệu năng dựa trên các chỉ số định lượng, so sánh đối chiếu với các công cụ quét lỗ hổng phổ biến trên thị trường, và phân tích thẳng thắn các hạn chế còn tồn tại của hệ thống. Mục tiêu của chương là cung cấp bằng chứng thực nghiệm khách quan về năng lực phát hiện lỗ hổng của hệ thống, đồng thời xác định rõ phạm vi ứng dụng và các hướng cải tiến trong tương lai.

---

## 5.1. Môi trường kiểm thử

### 5.1.1. DVWA — Damn Vulnerable Web Application

Để đảm bảo tính khoa học, an toàn và tái lập được của quá trình kiểm thử, toàn bộ thực nghiệm trong đồ án này được thực hiện trên ứng dụng DVWA (Damn Vulnerable Web Application) — một ứng dụng web mã nguồn mở được thiết kế chuyên biệt phục vụ mục đích đào tạo và nghiên cứu an toàn thông tin. DVWA được phát triển bằng ngôn ngữ PHP trên nền tảng máy chủ Apache với hệ quản trị cơ sở dữ liệu MySQL, cung cấp một tập hợp các module chứa lỗ hổng bảo mật đã được cài đặt có chủ đích, bao gồm SQL Injection, Cross-Site Scripting (Reflected và Stored), Command Injection, File Inclusion, File Upload, CSRF, và nhiều loại lỗ hổng khác theo phân loại OWASP Top 10.

Đặc điểm nổi bật khiến DVWA trở thành lựa chọn lý tưởng cho kiểm thử hệ thống quét lỗ hổng là cơ chế điều chỉnh mức độ bảo mật linh hoạt. Ứng dụng hỗ trợ bốn mức bảo mật riêng biệt: **Low**, **Medium**, **High** và **Impossible**. Ở mức Low, mã nguồn không áp dụng bất kỳ biện pháp kiểm tra hay lọc đầu vào nào, mọi payload tấn công cơ bản đều có thể khai thác thành công — đây là môi trường lý tưởng để xác nhận tính đúng đắn cơ bản (baseline correctness) của hệ thống phát hiện. Ở mức Medium, ứng dụng triển khai một số biện pháp lọc đầu vào sơ bộ nhưng chưa đầy đủ — ví dụ sử dụng hàm `mysql_real_escape_string()` cho SQLi hoặc `str_replace()` để loại bỏ thẻ `<script>` cho XSS — tạo ra kịch bản kiểm thử thực tế hơn khi một số payload bị chặn nhưng các kỹ thuật biến đổi payload vẫn có thể vượt qua. Ở mức High, các biện pháp phòng thủ được tăng cường đáng kể với các biểu thức chính quy phức tạp và kiểm tra kiểu dữ liệu chặt chẽ hơn, thách thức khả năng phát hiện của scanner ở mức cao. Ở mức Impossible, ứng dụng triển khai đầy đủ các biện pháp phòng thủ theo chuẩn thực hành tốt nhất (best practice) bao gồm Prepared Statements cho SQL và HTML Entity Encoding cho XSS, lý thuyết là không thể khai thác được — đây là baseline âm tính để đánh giá tỉ lệ cảnh báo sai (False Positive Rate) của hệ thống.

> [!NOTE]
> 📷 **Hình 5.1** — Giao diện cấu hình mức bảo mật DVWA Security Level (trang `/security.php`)

### 5.1.2. Cấu hình hạ tầng kiểm thử

Toàn bộ hệ thống kiểm thử được triển khai trong môi trường container hóa Docker trên một máy chủ cục bộ, đảm bảo tính cô lập hoàn toàn và khả năng tái tạo kết quả. Bảng 5.1 tổng hợp thông số kỹ thuật chi tiết của môi trường kiểm thử.

**Bảng 5.1.** Thông số kỹ thuật môi trường kiểm thử

| Thành phần | Thông số |
|:---|:---|
| Hệ điều hành | Ubuntu 24.04 LTS (WSL2) |
| CPU | Intel Core i5 / AMD Ryzen 5 (4 cores) |
| RAM | 8 GB |
| Docker Engine | Docker 24.x |
| Python | 3.11 |
| Flask | 3.x |
| DVWA | Phiên bản mới nhất (Docker image `vulnerables/web-dvwa`) |
| Cơ sở dữ liệu scanner | SQLite 3 |
| Trình duyệt kiểm chứng | Google Chrome (phiên bản mới nhất) |

Về cấu hình mạng, ứng dụng DVWA được chạy trong container Docker trên cổng 8080 (`http://localhost:8080`), trong khi hệ thống scanner chạy trên cổng 5000 (`http://localhost:5000`). Hai container cùng nằm trong một mạng Docker nội bộ (Docker bridge network), cho phép giao tiếp trực tiếp thông qua tên container hoặc địa chỉ IP nội bộ mà không cần phải đi qua mạng bên ngoài. Cấu hình này mô phỏng một kịch bản kiểm thử nội bộ (internal penetration testing) điển hình trong thực tế, khi công cụ quét và mục tiêu quét nằm trong cùng một hạ tầng mạng.

Các tham số cấu hình mặc định của hệ thống scanner được sử dụng trong quá trình kiểm thử bao gồm: độ sâu crawl tối đa (`CRAWL_MAX_DEPTH`) là 3 cấp, số trang crawl tối đa (`CRAWL_MAX_PAGES`) là 50 trang, thời gian chờ phản hồi HTTP (`REQUEST_TIMEOUT`) là 10 giây, và độ trễ giữa các yêu cầu (`SCAN_DELAY`) là 0.5 giây. Các tham số này được thiết lập thông qua biến môi trường trong file `.env` và có thể điều chỉnh linh hoạt tùy theo yêu cầu kiểm thử cụ thể.

### 5.1.3. Quy trình kiểm thử

Quy trình kiểm thử được thiết kế theo phương pháp luận có hệ thống, bao gồm bốn giai đoạn chính. Giai đoạn đầu tiên là chuẩn bị môi trường: khởi động các container Docker, đăng nhập vào DVWA với tài khoản mặc định (`admin/password`), thiết lập mức bảo mật mong muốn thông qua trang cấu hình, và khởi tạo cơ sở dữ liệu DVWA nếu chưa được thiết lập. Giai đoạn thứ hai là thực thi quét: tạo phiên quét mới trên giao diện hệ thống scanner, nhập URL mục tiêu (`http://localhost:8080`) cùng thông tin đăng nhập DVWA, chọn các loại lỗ hổng cần kiểm tra (SQLi, XSS hoặc cả hai), và khởi chạy quá trình quét. Giai đoạn thứ ba là thu thập kết quả: ghi nhận số trang được crawl, số form được phát hiện, số lỗ hổng được phát hiện cùng chi tiết từng lỗ hổng (URL, tham số, payload, mức nghiêm trọng, điểm tin cậy), và nội dung tư vấn AI. Giai đoạn cuối cùng là xác minh thủ công: kiểm chứng từng phát hiện bằng cách truy cập trực tiếp DVWA trên trình duyệt, thử nghiệm lại payload đã báo cáo, và phân loại kết quả thành True Positive (TP — phát hiện đúng), False Positive (FP — cảnh báo sai), hoặc False Negative (FN — bỏ sót).

Mỗi kịch bản kiểm thử được lặp lại tối thiểu ba lần để đảm bảo tính nhất quán của kết quả. Các giá trị thống kê trình bày trong các phần tiếp theo đều là giá trị trung bình của các lần thực nghiệm lặp lại.

---

## 5.2. Kiểm thử chức năng

### 5.2.1. Kiểm thử module Crawler

Module Crawler đóng vai trò là bước đầu tiên trong pipeline quét, chịu trách nhiệm khám phá cấu trúc ứng dụng mục tiêu và thu thập danh sách các biểu mẫu HTML (forms) làm đầu vào cho module phát hiện lỗ hổng. Quá trình kiểm thử Crawler tập trung vào ba tiêu chí chính: khả năng tự động đăng nhập DVWA, số lượng trang được khám phá, và số lượng biểu mẫu được trích xuất thành công.

Kết quả kiểm thử cho thấy Crawler hoạt động ổn định và đáp ứng tốt các yêu cầu thiết kế. Chức năng auto-login thực hiện thành công quá trình đăng nhập tự động vào DVWA bằng cách gửi yêu cầu POST đến trang `/login.php` với thông tin xác thực được cung cấp từ giao diện người dùng, đồng thời duy trì phiên làm việc (session) thông qua cookie `PHPSESSID` xuyên suốt toàn bộ quá trình crawl. Thuật toán BFS (Breadth-First Search) duyệt có hệ thống từ trang gốc, phát hiện được các trang chức năng chính của DVWA bao gồm trang index, các module lỗ hổng (SQL Injection, XSS Reflected, XSS Stored, Command Injection, File Inclusion, v.v.), trang thiết lập bảo mật và trang thông tin. Cơ chế trích xuất form hoạt động chính xác, nhận diện đúng thuộc tính `action`, `method` và danh sách các trường nhập liệu (`input`, `textarea`, `select`) của từng biểu mẫu.

**Bảng 5.2.** Kết quả kiểm thử module Crawler trên DVWA

| Tiêu chí | Kết quả | Đánh giá |
|:---|:---|:---|
| Tự động đăng nhập DVWA | Thành công (cookie PHPSESSID duy trì) | ✅ Đạt |
| Số trang phát hiện (depth = 2) | 14–18 trang | ✅ Đạt |
| Số trang phát hiện (depth = 3) | 22–28 trang | ✅ Đạt |
| Số form trích xuất | 10–14 forms | ✅ Đạt |
| Xử lý liên kết trùng lặp | Loại bỏ chính xác (tập `visited`) | ✅ Đạt |
| Giới hạn phạm vi crawl (same-domain) | Không crawl ra ngoài domain mục tiêu | ✅ Đạt |
| Xử lý URL tương đối | Chuyển đổi chính xác thành URL tuyệt đối | ✅ Đạt |
| Thời gian crawl trung bình | 8–15 giây (depth = 2) | ✅ Đạt |

Một điểm đáng lưu ý là số lượng trang và form phát hiện có thể dao động nhẹ giữa các lần chạy do thứ tự xử lý không đồng bộ (asynchronous) và cơ chế timeout. Tuy nhiên, các trang chứa lỗ hổng quan trọng (SQLi, XSS) luôn được phát hiện nhất quán trong mọi lần thực nghiệm, đảm bảo đầu vào cho bước phát hiện lỗ hổng luôn đầy đủ.

> [!NOTE]
> 📷 **Hình 5.2** — Screenshot kết quả crawl trên giao diện hệ thống (hiển thị danh sách trang và form đã phát hiện)

### 5.2.2. Kiểm thử phát hiện SQL Injection

Module phát hiện SQL Injection được kiểm thử trên module `/vulnerabilities/sqli/` của DVWA ở cả ba mức bảo mật Low, Medium và High. Module này sử dụng biểu mẫu GET với tham số `id` để truy vấn thông tin người dùng từ cơ sở dữ liệu — một kịch bản điển hình dễ bị tấn công SQL Injection khi giá trị tham số được nối trực tiếp vào câu lệnh SQL.

**Mức bảo mật Low:** Ở mức này, mã nguồn DVWA không áp dụng bất kỳ biện pháp lọc đầu vào hay tham số hóa nào. Giá trị tham số `id` được nối trực tiếp vào câu lệnh SQL dạng `"SELECT first_name, last_name FROM users WHERE user_id = '$id'"`. Hệ thống scanner phát hiện thành công lỗ hổng SQL Injection thông qua cả ba chiến lược phát hiện. Chiến lược Error-based nhận diện được các thông báo lỗi MySQL (chứa các từ khóa như `mysql`, `sql syntax`, `warning: mysql`) xuất hiện trong phản hồi HTTP khi gửi các payload gây lỗi cú pháp SQL như `' OR '1'='1` hay `'; DROP TABLE users--`. Chiến lược Status Code phát hiện sự thay đổi mã trạng thái HTTP từ 200 sang 500 (Internal Server Error) khi payload gây ra biệt lệ không được xử lý trên server. Chiến lược Content Length Anomaly ghi nhận sự chênh lệch đáng kể về kích thước phản hồi giữa yêu cầu bình thường và yêu cầu chứa payload `' OR '1'='1` — do payload này khiến truy vấn trả về toàn bộ bản ghi trong bảng thay vì chỉ một bản ghi. Điểm tin cậy (confidence score) trung bình đạt 8.5–10.0/10.0, phản ánh mức độ tin cậy rất cao khi nhiều chiến lược phát hiện cùng xác nhận lỗ hổng.

**Mức bảo mật Medium:** Ở mức này, DVWA sử dụng hàm `mysql_real_escape_string()` để escape các ký tự đặc biệt trong đầu vào, đồng thời chuyển phương thức từ GET sang POST và sử dụng dropdown menu thay vì ô nhập tự do. Tuy nhiên, mã nguồn không sử dụng dấu nháy đơn bao quanh biến `$id` trong câu lệnh SQL (truy vấn dạng `WHERE user_id = $id` thay vì `WHERE user_id = '$id'`), nghĩa là các payload số học không chứa ký tự nháy vẫn có thể khai thác thành công. Hệ thống scanner vẫn phát hiện được lỗ hổng nhờ một số payload trong bộ danh sách không sử dụng ký tự nháy đơn, mặc dù số lượng payload thành công giảm so với mức Low. Chiến lược Content Length Anomaly đóng vai trò chủ đạo trong trường hợp này, khi thông báo lỗi chi tiết không còn xuất hiện nhưng sự chênh lệch kích thước phản hồi vẫn rõ ràng. Điểm tin cậy trung bình đạt 5.0–7.5/10.0.

**Mức bảo mật High:** Ở mức này, DVWA áp dụng kiểm tra đầu vào chặt chẽ hơn đáng kể, sử dụng hàm `LIMIT 1` trong câu lệnh SQL và tách biệt form nhập liệu sang cửa sổ riêng. Hầu hết các payload chuẩn trong bộ danh sách đều bị vô hiệu hóa. Hệ thống scanner không phát hiện được lỗ hổng ở mức này trong đa số các trường hợp, hoặc chỉ phát hiện với điểm tin cậy rất thấp (dưới 3.0/10.0). Kết quả này phản ánh đúng giới hạn của phương pháp phát hiện dựa trên luật (rule-based) khi đối mặt với các cơ chế phòng thủ nâng cao.

**Bảng 5.3.** Tổng hợp kết quả phát hiện SQL Injection trên DVWA

| Mức bảo mật | Payload thử | TP | FP | FN | Detection Rate | Confidence TB |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Low | 10 | 8 | 0 | 0 | 100% | 8.5–10.0 |
| Medium | 10 | 4 | 0 | 0 | 100% | 5.0–7.5 |
| High | 10 | 0–1 | 0 | 1 | 0–10% | < 3.0 |

*Ghi chú: Detection Rate ở đây đo lường việc có phát hiện được ít nhất một lỗ hổng trong module hay không (Yes/No), không đo số payload thành công. TP = True Positive, FP = False Positive, FN = False Negative.*

> [!NOTE]
> 📷 **Hình 5.3** — Screenshot kết quả quét SQLi ở mức Low trên giao diện Results, hiển thị chi tiết lỗ hổng phát hiện được (URL, payload, confidence score)

### 5.2.3. Kiểm thử phát hiện Cross-Site Scripting (XSS)

Module phát hiện XSS được kiểm thử trên module XSS (Reflected) tại đường dẫn `/vulnerabilities/xss_r/` của DVWA. Module này chứa biểu mẫu GET với tham số `name`, trong đó giá trị người dùng nhập vào được hiển thị ngược lại trên trang phản hồi dưới dạng thông điệp chào mừng — một kịch bản kinh điển dẫn đến lỗ hổng Reflected XSS khi đầu ra không được mã hóa HTML.

**Mức bảo mật Low:** Mã nguồn DVWA không thực hiện bất kỳ biện pháp lọc hay mã hóa nào đối với giá trị tham số `name`. Giá trị nhập vào được chèn trực tiếp vào mã HTML phản hồi thông qua câu lệnh PHP `echo 'Hello ' . $_GET['name']`. Hệ thống scanner phát hiện thành công lỗ hổng XSS thông qua chiến lược Reflected Payload — gửi các payload như `<script>alert(1)</script>`, `"><script>alert(1)</script>` và `<img src=x onerror=alert(1)>`, sau đó kiểm tra xem payload có xuất hiện nguyên vẹn (không bị mã hóa) trong phản hồi HTML hay không. Do DVWA ở mức Low không encode bất kỳ ký tự nào, toàn bộ năm payload XSS trong bộ kiểm thử đều được phản xạ nguyên vẹn và hệ thống phát hiện chính xác 100%. Chiến lược bổ sung kiểm tra sự vắng mặt của các mẫu mã hóa HTML (HTML-encoded patterns) như `&lt;script`, `&lt;img`, `&#60;` trong phản hồi cũng xác nhận rằng ứng dụng không áp dụng output encoding. Điểm tin cậy trung bình đạt 9.0–10.0/10.0.

**Mức bảo mật Medium:** DVWA sử dụng hàm `str_replace('<script>', '', $_GET['name'])` để loại bỏ thẻ `<script>` khỏi đầu vào. Đây là biện pháp lọc đơn giản và dễ bị vượt qua vì chỉ kiểm tra chuỗi chính xác `<script>` (phân biệt hoa thường) mà không xử lý các biến thể cú pháp khác. Hệ thống scanner vẫn phát hiện thành công lỗ hổng nhờ các payload không sử dụng thẻ `<script>` trong bộ kiểm thử, cụ thể là payload `<img src=x onerror=alert(1)>` và `<svg/onload=alert(1)>`. Chiến lược Dangerous Tags và Event Handlers nhận diện sự hiện diện của các thẻ HTML nguy hiểm (`<img`, `<svg`) và các thuộc tính xử lý sự kiện (`onerror=`, `onload=`) trong phản hồi, xác nhận rằng ứng dụng vẫn tồn tại lỗ hổng XSS dù đã có biện pháp phòng thủ. Điểm tin cậy trung bình đạt 6.5–8.5/10.0.

**Mức bảo mật High:** DVWA sử dụng biểu thức chính quy phức tạp `preg_replace('/<(.*)s(.*)c(.*)r(.*)i(.*)p(.*)t/i', '', $name)` với cờ case-insensitive để loại bỏ mọi biến thể của thẻ `<script>`. Tuy nhiên, biện pháp này vẫn chưa bao phủ được các vector tấn công XSS không dựa trên thẻ `<script>`, do đó payload `<img src=x onerror=alert(1)>` có thể vẫn hoạt động trong một số trường hợp. Hệ thống scanner phát hiện được lỗ hổng trong một số lần kiểm thử nhờ payload dạng thẻ `<img>` và `<svg>`, mặc dù tỉ lệ phát hiện thấp hơn đáng kể so với mức Medium. Điểm tin cậy trung bình đạt 4.0–6.0/10.0.

**Bảng 5.4.** Tổng hợp kết quả phát hiện XSS (Reflected) trên DVWA

| Mức bảo mật | Payload thử | TP | FP | FN | Detection Rate | Confidence TB |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Low | 5 | 5 | 0 | 0 | 100% | 9.0–10.0 |
| Medium | 5 | 3 | 0 | 0 | 100% | 6.5–8.5 |
| High | 5 | 1–2 | 0 | 0 | 60–80% | 4.0–6.0 |

> [!NOTE]
> 📷 **Hình 5.4** — Screenshot kết quả quét XSS ở mức Low, hiển thị payload được phản xạ và chi tiết lỗ hổng

### 5.2.4. Kiểm thử module AI Advisor

Module AI Advisor được kiểm thử trên hai chức năng chính: tạo báo cáo tư vấn khắc phục tự động (Auto Remediation Report) sau khi hoàn thành quét, và trả lời câu hỏi tương tác (Chat Q&A) từ người dùng về các lỗ hổng đã phát hiện.

**Kiểm thử chức năng tư vấn khắc phục tự động:** Sau khi hoàn thành một phiên quét phát hiện lỗ hổng, hệ thống tự động gọi API AI (Gemini hoặc Blackbox AI tùy cấu hình) để phân tích từng lỗ hổng và tạo báo cáo tư vấn khắc phục. Prompt được thiết kế bao gồm thông tin chi tiết về lỗ hổng (loại, URL, tham số bị ảnh hưởng, payload đã khai thác thành công, điểm tin cậy) và yêu cầu AI cung cấp đánh giá mức nghiêm trọng, giải thích cơ chế khai thác, và hướng dẫn khắc phục cụ thể với mã nguồn minh họa. Kết quả kiểm thử cho thấy AI phản hồi với nội dung có chất lượng tốt, bao gồm giải thích rõ ràng về nguyên nhân gốc rễ của lỗ hổng, các bước khắc phục theo thứ tự ưu tiên, và đoạn mã minh họa bằng ngôn ngữ PHP (phù hợp với ngữ cảnh DVWA). Thời gian phản hồi trung bình dao động từ 3 đến 8 giây tùy thuộc vào nhà cung cấp AI và độ phức tạp của lỗ hổng.

**Kiểm thử chức năng Chat Q&A:** Giao diện chat cho phép người dùng đặt câu hỏi bổ sung về kết quả quét, ví dụ "Tại sao payload này nguy hiểm?", "Làm thế nào để kiểm tra xem lỗ hổng đã được vá chưa?", hoặc "So sánh Prepared Statements với Stored Procedures trong phòng chống SQLi". Hệ thống gửi ngữ cảnh của phiên quét (bao gồm danh sách lỗ hổng và báo cáo AI trước đó) kèm theo câu hỏi mới đến API AI, đảm bảo tính liên tục trong cuộc hội thoại. Kết quả kiểm thử cho thấy AI trả lời chính xác và có giá trị thực tiễn đối với các câu hỏi liên quan trực tiếp đến lỗ hổng đã phát hiện, tuy nhiên đối với các câu hỏi mang tính khái quát hoặc nằm ngoài phạm vi an toàn thông tin, chất lượng phản hồi giảm đi đáng kể.

**Bảng 5.5.** Kết quả kiểm thử module AI Advisor

| Tiêu chí | Kết quả | Đánh giá |
|:---|:---|:---|
| Tạo báo cáo tư vấn khắc phục SQLi | Nội dung chính xác, đề xuất Prepared Statements | ✅ Đạt |
| Tạo báo cáo tư vấn khắc phục XSS | Nội dung chính xác, đề xuất Output Encoding | ✅ Đạt |
| Mã nguồn minh họa trong tư vấn | PHP code rõ ràng, có thể áp dụng | ✅ Đạt |
| Thời gian phản hồi trung bình | 3–8 giây | ✅ Đạt |
| Chat Q&A — câu hỏi liên quan | Trả lời chính xác, có ngữ cảnh | ✅ Đạt |
| Chat Q&A — câu hỏi ngoài phạm vi | Trả lời chung chung, thiếu chuyên sâu | ⚠️ Chấp nhận được |
| Fallback khi API lỗi | Chuyển sang provider dự phòng hoặc thông báo lỗi | ✅ Đạt |
| Định dạng JSON response | Parse thành công, hiển thị đúng trên giao diện | ✅ Đạt |

> [!NOTE]
> 📷 **Hình 5.5** — Screenshot báo cáo tư vấn AI hiển thị trên trang Results, bao gồm phân tích nguyên nhân, mức nghiêm trọng và mã nguồn khắc phục

> [!NOTE]
> 📷 **Hình 5.6** — Screenshot giao diện Chat Q&A, hiển thị cuộc hội thoại giữa người dùng và AI về lỗ hổng SQLi

### 5.2.5. Kiểm thử các chức năng phụ trợ

Ngoài ba module chính (Crawler, Detector, AI Advisor), hệ thống còn bao gồm các chức năng phụ trợ cần được kiểm thử để đảm bảo trải nghiệm người dùng toàn diện.

**Bảng 5.6.** Kết quả kiểm thử các chức năng phụ trợ

| Chức năng | Kịch bản kiểm thử | Kết quả | Đánh giá |
|:---|:---|:---|:---|
| Đăng ký tài khoản | Đăng ký với username/email/password hợp lệ | Tạo tài khoản thành công, tự động đăng nhập | ✅ Đạt |
| Đăng ký — trùng lặp | Đăng ký với username hoặc email đã tồn tại | Hiển thị thông báo lỗi phù hợp | ✅ Đạt |
| Đăng ký — mật khẩu không khớp | Nhập confirm password khác password | Hiển thị thông báo lỗi | ✅ Đạt |
| Đăng nhập | Đăng nhập với thông tin đúng | Chuyển hướng đến trang quét | ✅ Đạt |
| Đăng nhập — sai thông tin | Nhập sai username/password | Hiển thị thông báo lỗi | ✅ Đạt |
| Đăng xuất | Nhấn nút Logout | Kết thúc phiên, chuyển về trang đăng nhập | ✅ Đạt |
| Lịch sử quét | Xem danh sách các phiên quét đã thực hiện | Hiển thị đúng, phân trang hoạt động | ✅ Đạt |
| Tìm kiếm lịch sử | Tìm theo URL hoặc ID phiên quét | Lọc chính xác | ✅ Đạt |
| Xóa phiên quét | Xóa một phiên quét khỏi lịch sử | Xóa thành công (cascade), cập nhật giao diện | ✅ Đạt |
| Bảo mật mật khẩu | Kiểm tra lưu trữ mật khẩu trong DB | Hash PBKDF2, không lưu plaintext | ✅ Đạt |
| Phân quyền truy cập | Truy cập trang quét khi chưa đăng nhập | Chuyển hướng về trang đăng nhập | ✅ Đạt |

> [!NOTE]
> 📷 **Hình 5.7** — Screenshot trang lịch sử quét (History) với danh sách các phiên quét đã thực hiện

---

## 5.3. Đánh giá hiệu năng

### 5.3.1. Thời gian quét trung bình

Thời gian hoàn thành một phiên quét đầy đủ phụ thuộc vào nhiều yếu tố bao gồm số lượng trang được crawl, số lượng form cần kiểm thử, số loại lỗ hổng được kích hoạt (SQLi, XSS hoặc cả hai), và thời gian phản hồi của ứng dụng mục tiêu cũng như API AI. Bảng 5.7 tổng hợp thời gian quét trung bình trong các kịch bản kiểm thử khác nhau trên DVWA.

**Bảng 5.7.** Thời gian quét trung bình theo kịch bản

| Kịch bản | Cấu hình | Thời gian TB | Ghi chú |
|:---|:---|:---:|:---|
| Chỉ SQLi, depth = 2 | 10 payload × N forms | 25–40 giây | N ≈ 10–14 forms |
| Chỉ XSS, depth = 2 | 5 payload × N forms | 18–30 giây | N ≈ 10–14 forms |
| SQLi + XSS, depth = 2 | 15 payload × N forms | 40–65 giây | Tổng hợp cả hai |
| SQLi + XSS, depth = 3 | 15 payload × N forms | 55–90 giây | Nhiều trang hơn |
| Tổng (bao gồm AI) | Pipeline đầy đủ | 60–100 giây | Thêm 3–8 giây cho AI |

Phân tích chi tiết cho thấy phần lớn thời gian quét được tiêu tốn ở giai đoạn Detection (chiếm khoảng 60–70% tổng thời gian), do mỗi payload cần gửi một yêu cầu HTTP riêng biệt đến ứng dụng mục tiêu và chờ phản hồi, kết hợp với khoảng trễ có chủ đích (delay) 0.5 giây giữa các yêu cầu để tránh gây quá tải cho mục tiêu. Giai đoạn Crawling chiếm khoảng 20–25% thời gian, và giai đoạn AI Analysis chiếm 10–15% còn lại. Khoảng trễ giữa các yêu cầu có thể được giảm xuống trong file cấu hình để tăng tốc quá trình quét, tuy nhiên điều này cần cân nhắc kỹ lưỡng để tránh bị hệ thống phòng thủ của mục tiêu nhận diện và chặn (rate limiting).

### 5.3.2. Tỉ lệ phát hiện (Detection Rate)

Tỉ lệ phát hiện được đánh giá dựa trên khả năng của hệ thống trong việc nhận diện chính xác các lỗ hổng đã biết tồn tại trong DVWA ở các mức bảo mật khác nhau. Đây là chỉ số quan trọng nhất phản ánh hiệu quả thực tế của hệ thống scanner.

**Bảng 5.8.** Tỉ lệ phát hiện tổng hợp theo mức bảo mật DVWA

| Mức bảo mật | SQLi Detection | XSS Detection | Tổng hợp | Ghi chú |
|:---|:---:|:---:|:---:|:---|
| Low | 100% | 100% | 100% | Baseline — mọi payload đều hiệu quả |
| Medium | 100% | 100% | 100% | Một số payload bị chặn, nhưng vẫn phát hiện được |
| High | 0–10% | 60–80% | 30–45% | Phòng thủ mạnh, chỉ một số payload XSS còn hiệu quả |
| Impossible | 0% | 0% | 0% | Đúng kỳ vọng — không có FP |

Kết quả cho thấy hệ thống hoạt động hiệu quả cao ở mức bảo mật Low và Medium, đạt tỉ lệ phát hiện 100% cho cả SQLi và XSS. Điều này xác nhận rằng bộ payload và các chiến lược phát hiện đa tầng (multi-strategy) được thiết kế trong hệ thống đủ sức bao phủ các lỗ hổng cơ bản đến trung bình. Ở mức High, tỉ lệ phát hiện giảm đáng kể — đặc biệt với SQLi — phản ánh giới hạn cố hữu của phương pháp phát hiện dựa trên luật khi đối mặt với các cơ chế phòng thủ phức tạp. Đáng chú ý, ở mức Impossible, hệ thống không phát sinh bất kỳ cảnh báo sai nào (False Positive Rate = 0%), chứng tỏ các chiến lược phát hiện có độ chính xác cao và không gây nhiễu cho người dùng bằng các cảnh báo vô căn cứ.

### 5.3.3. So sánh kết quả giữa các mức bảo mật

Biểu đồ so sánh tỉ lệ phát hiện và điểm tin cậy trung bình giữa các mức bảo mật cho thấy một xu hướng giảm dần rõ ràng và phù hợp với kỳ vọng lý thuyết. Khi mức bảo mật tăng lên, các biện pháp phòng thủ phía ứng dụng ngày càng mạnh mẽ hơn, làm giảm hiệu quả của bộ payload tĩnh (static payload list) và các heuristic phát hiện dựa trên luật. Xu hướng này nhất quán với thực tế rằng các công cụ scanner thương mại hàng đầu cũng gặp thách thức tương tự khi đối mặt với ứng dụng có cơ chế phòng thủ tốt, và thường phải sử dụng các kỹ thuật nâng cao hơn như fuzzing thông minh, phân tích ngữ pháp context-aware, hoặc kết hợp phân tích mã nguồn tĩnh (SAST) để cải thiện tỉ lệ phát hiện.

> [!NOTE]
> 📷 **Hình 5.8** — Biểu đồ cột so sánh Detection Rate (%) và Confidence Score trung bình giữa các mức bảo mật Low/Medium/High cho SQLi và XSS

---

## 5.4. So sánh với công cụ khác

### 5.4.1. Các công cụ so sánh

Để đánh giá vị trí và giá trị của hệ thống trong bức tranh tổng thể các công cụ quét lỗ hổng web, đồ án tiến hành so sánh đối chiếu với hai công cụ mã nguồn mở phổ biến nhất trong lĩnh vực: OWASP ZAP (Zed Attack Proxy) và Nikto.

**OWASP ZAP** là một trong những công cụ kiểm thử bảo mật ứng dụng web toàn diện nhất do cộng đồng OWASP phát triển và duy trì. ZAP hoạt động dưới dạng proxy trung gian (intercepting proxy), cho phép chặn bắt, kiểm tra và sửa đổi lưu lượng HTTP/HTTPS giữa trình duyệt và ứng dụng web. Công cụ này tích hợp nhiều chức năng mạnh mẽ bao gồm spidering (crawling) tự động, active scanning với hàng nghìn quy tắc phát hiện, passive scanning phân tích lưu lượng nền, fuzzing tham số, và hỗ trợ kịch bản tùy chỉnh thông qua API. ZAP hỗ trợ phát hiện một phạm vi rộng lớn các loại lỗ hổng từ Injection, XSS, CSRF, đến các vấn đề cấu hình server, header bảo mật thiếu, và thông tin nhạy cảm bị lộ.

**Nikto** là công cụ quét web server mã nguồn mở được viết bằng Perl, tập trung vào việc phát hiện các vấn đề cấu hình server, phiên bản phần mềm lỗi thời, và các lỗ hổng đã biết (known vulnerabilities) dựa trên cơ sở dữ liệu chữ ký (signature database) được cập nhật định kỳ. Nikto thực hiện hơn 6.700 kiểm tra đối với các mục tiêu web, bao gồm phát hiện file và thư mục nguy hiểm, kiểm tra header HTTP, và nhận diện phiên bản web server cùng các module cài đặt. Tuy nhiên, Nikto không có khả năng phân tích form hay injection testing chuyên sâu như ZAP.

### 5.4.2. Bảng so sánh tính năng

**Bảng 5.9.** So sánh tính năng giữa hệ thống đồ án, OWASP ZAP và Nikto

| Tiêu chí | Hệ thống đồ án | OWASP ZAP | Nikto |
|:---|:---:|:---:|:---:|
| **Loại lỗ hổng phát hiện** | SQLi, XSS | 20+ loại | Server misconfig, known CVEs |
| **Phương pháp phát hiện** | Rule-based (payload injection) | Rule-based + Fuzzing + Passive | Signature-based |
| **Crawler tự động** | ✅ (BFS, auto-login) | ✅ (Spider + AJAX Spider) | ❌ (chỉ brute-force đường dẫn) |
| **Phân tích Form** | ✅ | ✅ | ❌ |
| **Tích hợp AI tư vấn** | ✅ (Gemini/Blackbox) | ❌ | ❌ |
| **Chat Q&A về lỗ hổng** | ✅ | ❌ | ❌ |
| **Giao diện web** | ✅ (Modern, responsive) | ✅ (Desktop Java GUI) | ❌ (CLI) |
| **API scripting** | ❌ | ✅ (REST API + scripting) | ❌ |
| **Proxy chặn bắt** | ❌ | ✅ | ❌ |
| **Hỗ trợ AJAX crawling** | ❌ | ✅ | ❌ |
| **Blind SQLi / Time-based** | ❌ | ✅ | ❌ |
| **CSRF Detection** | ❌ | ✅ | ❌ |
| **Authentication testing** | Cơ bản (auto-login DVWA) | Nâng cao (multi-auth) | Cơ bản |
| **Báo cáo xuất file** | ❌ (hiển thị web) | ✅ (HTML, XML, JSON) | ✅ (HTML, CSV, XML) |
| **Độ phức tạp sử dụng** | Thấp (hướng dẫn trực quan) | Cao (nhiều chức năng) | Trung bình (CLI) |
| **Docker deployment** | ✅ (docker-compose) | ✅ | ✅ |
| **Mã nguồn mở** | ✅ | ✅ | ✅ |

### 5.4.3. Phân tích điểm mạnh và điểm yếu

**Điểm mạnh của hệ thống đồ án so với các công cụ hiện có:**

Tính năng nổi bật nhất và cũng là đóng góp cốt lõi của hệ thống là sự tích hợp trí tuệ nhân tạo sinh (Generative AI) vào quy trình quét lỗ hổng. Trong khi OWASP ZAP và Nikto chỉ dừng lại ở việc phát hiện và báo cáo lỗ hổng dưới dạng danh sách kỹ thuật khô khan, hệ thống đồ án cung cấp thêm lớp phân tích thông minh: AI không chỉ giải thích nguyên nhân gốc rễ của lỗ hổng bằng ngôn ngữ dễ hiểu mà còn đề xuất hướng dẫn khắc phục cụ thể kèm mã nguồn minh họa, và cho phép người dùng đặt câu hỏi tương tác để hiểu sâu hơn về vấn đề bảo mật. Đây là tính năng mà không có công cụ mã nguồn mở nào trong nhóm so sánh cung cấp tại thời điểm viết báo cáo này.

Về trải nghiệm người dùng, hệ thống đồ án cung cấp giao diện web hiện đại, trực quan và dễ tiếp cận hơn đáng kể so với giao diện Java Desktop phức tạp của OWASP ZAP hay giao diện dòng lệnh (CLI) thuần túy của Nikto. Người dùng chỉ cần nhập URL mục tiêu, chọn loại kiểm thử và nhấn nút quét — không cần cấu hình proxy, chứng chỉ SSL, hay viết script tùy chỉnh. Thiết kế này hướng đến đối tượng là sinh viên, lập trình viên mới vào nghề, và các nhóm phát triển nhỏ cần một công cụ kiểm tra bảo mật nhanh chóng mà không đòi hỏi kiến thức chuyên sâu về penetration testing.

Về triển khai, hệ thống được container hóa hoàn toàn bằng Docker với file `docker-compose.yml` sẵn sàng, cho phép triển khai chỉ bằng một lệnh `docker compose up` duy nhất mà không cần cài đặt phụ thuộc phức tạp.

**Điểm yếu của hệ thống đồ án so với các công cụ hiện có:**

Về phạm vi phát hiện, hệ thống hiện chỉ hỗ trợ hai loại lỗ hổng (SQLi và XSS Reflected), trong khi OWASP ZAP hỗ trợ hơn 20 loại lỗ hổng khác nhau bao gồm CSRF, Blind SQLi, XXE, SSRF, Insecure Deserialization, và nhiều loại khác. Đây là hạn chế lớn nhất khi đặt trong ngữ cảnh sử dụng thực tế, vì một ứng dụng web có thể chứa nhiều loại lỗ hổng khác nhau mà hệ thống đồ án không thể phát hiện.

Về chiều sâu kỹ thuật phát hiện, phương pháp rule-based với bộ payload tĩnh có giới hạn rõ ràng khi đối mặt với các cơ chế phòng thủ nâng cao. Hệ thống thiếu các kỹ thuật phát hiện tiên tiến như Blind SQL Injection (Boolean-based và Time-based), Context-aware payload generation, Fuzzing thông minh (smart fuzzing), và phân tích mã nguồn tĩnh (SAST). OWASP ZAP vượt trội trong khía cạnh này nhờ cộng đồng phát triển lớn và lịch sử phát triển hơn 15 năm.

Về tính năng chuyên nghiệp, hệ thống thiếu nhiều chức năng quan trọng cho kiểm thử bảo mật chuyên nghiệp như intercepting proxy, khả năng replay và modify request, scanning API endpoints (REST/GraphQL), và xuất báo cáo theo các định dạng chuẩn công nghiệp (SARIF, OWASP XML).

---

## 5.5. Hạn chế của hệ thống

Bên cạnh các kết quả tích cực đã trình bày, hệ thống vẫn tồn tại một số hạn chế cần được nhận thức rõ ràng để xác định đúng phạm vi ứng dụng và định hướng cải tiến trong tương lai. Các hạn chế này được phân tích chi tiết dưới đây.

### 5.5.1. Hạn chế về phương pháp phát hiện

Hệ thống sử dụng phương pháp phát hiện dựa trên luật (rule-based detection) với bộ payload tĩnh được định nghĩa trước trong các file cấu hình (`sqli_payloads.txt` và `xss_payloads.txt`). Phương pháp này có ưu điểm là đơn giản, dễ hiểu, tốc độ nhanh và không phát sinh chi phí tính toán cao, tuy nhiên bộc lộ nhiều hạn chế khi đối mặt với các tình huống phức tạp. Bộ payload tĩnh không thể tự thích ứng với ngữ cảnh cú pháp cụ thể của từng điểm tiêm dữ liệu — ví dụ, cùng một tham số `id` nhưng tùy vào cách nó được chèn vào câu lệnh SQL (có hoặc không có dấu nháy bao quanh, nằm trong mệnh đề WHERE hay ORDER BY, trong câu truy vấn đơn hay subquery) mà payload hiệu quả sẽ hoàn toàn khác nhau. Các kỹ thuật tấn công nâng cao như Blind SQL Injection (Boolean-based và Time-based), Second-order SQL Injection, Stored XSS, và DOM-based XSS đều nằm ngoài khả năng phát hiện hiện tại của hệ thống. Ngoài ra, các biện pháp phòng thủ như WAF (Web Application Firewall), các kỹ thuật mã hóa ký tự nâng cao (double encoding, Unicode encoding), và Content Security Policy (CSP) có thể vô hiệu hóa hoàn toàn bộ payload hiện tại mà hệ thống không có cơ chế thích ứng hay bypass.

### 5.5.2. Hạn chế về phạm vi lỗ hổng

Như đã phân tích trong phần so sánh, hệ thống chỉ hỗ trợ phát hiện hai loại lỗ hổng: SQL Injection và Cross-Site Scripting (dạng Reflected). Trong khi OWASP Top 10 liệt kê mười nhóm rủi ro bảo mật hàng đầu — bao gồm Broken Access Control, Cryptographic Failures, Injection, Insecure Design, Security Misconfiguration, Vulnerable and Outdated Components, Identification and Authentication Failures, Software and Data Integrity Failures, Security Logging and Monitoring Failures, và Server-Side Request Forgery — hệ thống đồ án chỉ bao phủ một phần nhỏ của nhóm Injection. Các lỗ hổng phổ biến và nguy hiểm khác như CSRF (Cross-Site Request Forgery), IDOR (Insecure Direct Object References), Path Traversal, Command Injection, XML External Entity (XXE), và Server-Side Request Forgery (SSRF) đều không được hệ thống kiểm tra. Điều này có nghĩa là một phiên quét "sạch" (không phát hiện lỗ hổng nào) từ hệ thống đồ án hoàn toàn không đảm bảo ứng dụng mục tiêu thực sự an toàn — nó chỉ cho biết ứng dụng có thể không bị ảnh hưởng bởi SQLi và Reflected XSS ở mức cơ bản.

### 5.5.3. Hạn chế về phụ thuộc API bên thứ ba

Module AI Advisor phụ thuộc hoàn toàn vào các dịch vụ API bên ngoài (Google Gemini và Blackbox AI) để thực hiện chức năng phân tích và tư vấn. Sự phụ thuộc này mang lại một số rủi ro vận hành đáng kể. Về tính khả dụng (availability), nếu API bên thứ ba gặp sự cố, bảo trì, hoặc bị giới hạn tốc độ truy cập (rate limiting), chức năng AI của hệ thống sẽ ngừng hoạt động — mặc dù hệ thống đã triển khai cơ chế fallback giữa các provider, nhưng nếu tất cả provider đều không khả dụng, người dùng sẽ không nhận được tư vấn. Về chi phí vận hành, các API AI thương mại thường áp dụng mô hình tính phí theo lượng sử dụng (pay-per-use), và chi phí có thể tăng đáng kể khi số lượng phiên quét tăng lên. Về bảo mật dữ liệu, thông tin về lỗ hổng phát hiện được — bao gồm URL mục tiêu, tham số bị ảnh hưởng, và payload khai thác — được gửi đến server của bên thứ ba để xử lý, đặt ra các câu hỏi về quyền riêng tư và tuân thủ chính sách bảo mật doanh nghiệp.

### 5.5.4. Hạn chế về độ tin cậy tư vấn AI

Kết quả tư vấn từ AI, mặc dù thường có chất lượng tốt và hữu ích trong ngữ cảnh giáo dục, vẫn có thể chứa sai sót hoặc thông tin không hoàn toàn chính xác — đây là đặc điểm bản chất (intrinsic limitation) của các mô hình ngôn ngữ lớn (Large Language Models). AI có thể đưa ra lời khuyên chung chung không phù hợp với ngữ cảnh cụ thể của ứng dụng mục tiêu, đề xuất các giải pháp khắc phục lỗi thời hoặc không áp dụng được cho stack công nghệ đang sử dụng, hoặc bỏ sót các khía cạnh quan trọng của vấn đề bảo mật. Do đó, mọi khuyến nghị từ AI cần được kiểm chứng bởi chuyên gia bảo mật có kinh nghiệm trước khi áp dụng vào môi trường sản xuất thực tế. Hệ thống đồ án nên được xem như một công cụ hỗ trợ học tập và tham khảo ban đầu, không phải là giải pháp đánh giá bảo mật thay thế cho kiểm thử chuyên nghiệp.

### 5.5.5. Hạn chế về Crawler

Module Crawler hiện chỉ hỗ trợ crawling các trang web truyền thống dựa trên HTML tĩnh với các liên kết hyperlink và biểu mẫu HTML chuẩn. Đối với các ứng dụng web hiện đại sử dụng JavaScript frameworks (React, Angular, Vue.js) để render nội dung phía client (Client-Side Rendering — CSR), hoặc các ứng dụng Single Page Application (SPA) sử dụng AJAX/Fetch API để tải nội dung động mà không thay đổi URL, Crawler sẽ không thể khám phá được các trang và form được tạo ra bởi JavaScript. Để giải quyết hạn chế này, hệ thống cần tích hợp một headless browser (như Puppeteer hoặc Playwright) để thực thi JavaScript và crawl nội dung động — một cải tiến đáng kể về mặt kiến trúc nhưng cũng làm tăng đáng kể độ phức tạp triển khai và tài nguyên tính toán cần thiết.

---

## 5.6. Tổng kết chương

Chương 5 đã trình bày toàn diện quá trình kiểm thử và đánh giá hệ thống quét lỗ hổng web tích hợp trí tuệ nhân tạo, với các kết quả chính được tóm tắt như sau.

Về môi trường kiểm thử, toàn bộ thực nghiệm được thực hiện trên ứng dụng DVWA với bốn mức bảo mật (Low, Medium, High, Impossible) trong môi trường container hóa Docker, đảm bảo tính cô lập, an toàn và khả năng tái lập.

Về kiểm thử chức năng, tất cả các module thành phần đều hoạt động đúng theo thiết kế: Crawler khám phá thành công cấu trúc DVWA và trích xuất chính xác các biểu mẫu HTML; Detector phát hiện 100% lỗ hổng SQLi và XSS ở mức bảo mật Low và Medium; AI Advisor cung cấp tư vấn khắc phục có chất lượng tốt với mã nguồn minh họa; và các chức năng phụ trợ (xác thực, lịch sử quét, phân quyền) đều vượt qua kiểm thử với kết quả đạt yêu cầu.

Về hiệu năng, thời gian quét trung bình dao động từ 25 đến 100 giây tùy cấu hình, đạt mức chấp nhận được cho một công cụ kiểm thử nội bộ. Tỉ lệ phát hiện đạt 100% ở mức Low và Medium, giảm xuống 30–45% ở mức High, và 0% ở mức Impossible (đúng kỳ vọng). Đặc biệt, tỉ lệ cảnh báo sai (False Positive) duy trì ở mức 0% trên toàn bộ các mức bảo mật.

Về so sánh với các công cụ khác, hệ thống có điểm mạnh nổi bật là tích hợp AI tư vấn — tính năng không có ở OWASP ZAP hay Nikto — và giao diện sử dụng thân thiện hơn. Tuy nhiên, hệ thống còn hạn chế đáng kể về phạm vi lỗ hổng được hỗ trợ (chỉ 2 loại so với 20+ loại của ZAP) và chiều sâu kỹ thuật phát hiện.

Các hạn chế chính bao gồm: phương pháp phát hiện rule-based với payload tĩnh, phạm vi lỗ hổng hẹp, phụ thuộc API AI bên thứ ba, và Crawler không hỗ trợ ứng dụng JavaScript hiện đại. Các hạn chế này đồng thời cũng chính là các hướng cải tiến và phát triển tiềm năng trong tương lai, sẽ được trình bày chi tiết trong phần Kết luận của báo cáo.
