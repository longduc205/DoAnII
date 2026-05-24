# CHƯƠNG 4: TRIỂN KHAI HỆ THỐNG

Chương này trình bày chi tiết quá trình hiện thực hóa bản thiết kế kiến trúc và các đặc tả đã xây dựng trong Chương 3 thành mã nguồn hoạt động. Nội dung bao gồm việc mô tả cấu trúc tổ chức mã nguồn của dự án, phân tích từng module chức năng cốt lõi — Crawler, Detector (phát hiện SQL Injection và XSS), AI Advisor, và Scanner Engine — với giải thích logic xử lý, thuật toán áp dụng và minh họa bằng các đoạn mã nguồn Python tiêu biểu. Bên cạnh đó, chương cũng trình bày cách xây dựng giao diện người dùng với hệ thống template Jinja2, hiệu ứng hoạt ảnh và tương tác AJAX, cùng quy trình triển khai toàn bộ hệ thống trong môi trường container hóa Docker. Mỗi phần được trình bày theo trình tự phản ánh pipeline xử lý thực tế của hệ thống: thu thập dữ liệu → phát hiện lỗ hổng → phân tích bằng AI → điều phối tổng thể → hiển thị kết quả → đóng gói triển khai.

---

## 4.1. Cấu trúc mã nguồn

Dự án được tổ chức theo kiến trúc phân tầng đã thiết kế ở Mục 3.2.1, trong đó mỗi thư mục con tương ứng với một tầng hoặc một nhóm chức năng cụ thể, tuân thủ nguyên tắc phân tách mối quan tâm (Separation of Concerns) giúp mã nguồn dễ đọc, dễ bảo trì và dễ mở rộng. Cấu trúc cây thư mục tổng thể của dự án như sau:

```
DoAnII/
├── run.py                    # Điểm khởi chạy ứng dụng (Entry Point)
├── requirements.txt          # Danh sách thư viện Python phụ thuộc
├── Dockerfile                # Định nghĩa Docker image cho ứng dụng
├── docker-compose.yml        # Cấu hình đa container (Scanner + DVWA)
├── .env                      # Biến môi trường (API keys, cấu hình)
│
├── app/                      # Package chính của ứng dụng Flask
│   ├── __init__.py           # Application Factory (tạo Flask app)
│   ├── config.py             # Lớp cấu hình (Config class)
│   │
│   ├── models/               # Tầng Dữ liệu — ORM Models
│   │   ├── __init__.py       # Import tập trung các Model
│   │   ├── user.py           # Model User (xác thực)
│   │   ├── scan.py           # Model Scan (phiên quét)
│   │   ├── page.py           # Model Page (trang phát hiện)
│   │   ├── vulnerability.py  # Model Vulnerability (lỗ hổng)
│   │   ├── ai_result.py      # Model AIResult (phân tích AI)
│   │   └── chat_message.py   # Model ChatMessage (hội thoại Q&A)
│   │
│   ├── routes/               # Tầng Điều khiển — Flask Blueprints
│   │   ├── auth.py           # Blueprint xác thực (đăng nhập, đăng ký)
│   │   ├── scan.py           # Blueprint khởi tạo và quản lý quét
│   │   ├── results.py        # Blueprint hiển thị kết quả quét
│   │   ├── history.py        # Blueprint lịch sử phiên quét
│   │   ├── ai_chat.py        # Blueprint API hỏi đáp AI
│   │   ├── main.py           # Blueprint trang chủ
│   │   └── tasks.py          # Blueprint quản lý tác vụ
│   │
│   ├── services/             # Tầng Dịch vụ — Logic nghiệp vụ
│   │   ├── crawler.py        # Module Crawler (duyệt web BFS)
│   │   ├── detector.py       # Module Detector (phát hiện lỗ hổng)
│   │   ├── ai_advisor.py     # Module AI Advisor (tư vấn LLM)
│   │   └── scanner.py        # Scanner Engine (bộ điều phối)
│   │
│   ├── utils/                # Tiện ích dùng chung
│   │   ├── http_client.py    # HTTP Client wrapper với auto-login
│   │   ├── helpers.py        # Hàm trợ giúp chung
│   │   ├── logger.py         # Cấu hình logging
│   │   └── db_init.py        # Khởi tạo cơ sở dữ liệu
│   │
│   └── static/               # Tài nguyên tĩnh (CSS, JS, images)
│
├── templates/                # Tầng Trình bày — Template Jinja2
│   ├── base.html             # Template cơ sở (sidebar, header)
│   ├── login.html            # Trang đăng nhập
│   ├── register.html         # Trang đăng ký
│   ├── index.html            # Trang chủ
│   ├── scan.html             # Trang cấu hình quét
│   ├── results.html          # Trang kết quả chi tiết
│   ├── history.html          # Trang lịch sử quét
│   ├── profile.html          # Trang hồ sơ người dùng
│   └── tasks.html            # Trang quản lý tác vụ
│
├── data/                     # Dữ liệu tĩnh
│   └── payloads/             # Danh sách payload kiểm thử
│       ├── sqli_payloads.txt # 10 payload SQL Injection
│       └── xss_payloads.txt  # 10 payload XSS
│
└── instance/                 # Thư mục runtime (SQLite DB)
    └── scanner.db            # Cơ sở dữ liệu SQLite
```

Tệp `run.py` đóng vai trò điểm khởi chạy duy nhất (Single Entry Point) của toàn bộ ứng dụng. Nội dung tệp này rất ngắn gọn — chỉ gồm ba dòng lệnh thiết yếu: import hàm `create_app` từ package `app`, gọi hàm này để tạo đối tượng Flask application thông qua mẫu Application Factory, và khởi chạy development server trên cổng 5000 với chế độ debug. Sự đơn giản này phản ánh triết lý thiết kế của Flask: toàn bộ logic khởi tạo phức tạp (đăng ký Blueprint, cấu hình extension, tạo bảng cơ sở dữ liệu) được đóng gói bên trong hàm `create_app()` tại tệp `app/__init__.py`, giữ cho điểm khởi chạy sạch sẽ và dễ hiểu.

Thư mục `app/services/` là nơi tập trung toàn bộ logic nghiệp vụ cốt lõi, tách biệt hoàn toàn khỏi tầng Controller (routes) và tầng Data (models). Bốn module dịch vụ — `crawler.py`, `detector.py`, `ai_advisor.py` và `scanner.py` — được thiết kế dưới dạng các class Python độc lập, mỗi class đảm nhận một trách nhiệm duy nhất (Single Responsibility Principle) và giao tiếp với nhau thông qua các cấu trúc dữ liệu Python chuẩn (dictionary, list) thay vì phụ thuộc trực tiếp vào ORM Model hay HTTP request/response. Cách tổ chức này cho phép mỗi module có thể được kiểm thử đơn vị (Unit Testing) độc lập mà không cần khởi tạo Flask application context hay kết nối cơ sở dữ liệu.

Thư mục `data/payloads/` chứa hai tệp văn bản liệt kê các chuỗi payload kiểm thử — mỗi payload nằm trên một dòng riêng biệt, các dòng bắt đầu bằng ký tự `#` được coi là chú thích và bị bỏ qua khi tải. Việc tách danh sách payload ra khỏi mã nguồn Python và lưu trữ trong tệp ngoài mang lại hai lợi ích: thứ nhất, cho phép cập nhật, bổ sung hoặc thay thế bộ payload mà không cần sửa đổi và triển khai lại mã nguồn; thứ hai, tạo điều kiện cho người dùng nâng cao có thể tùy chỉnh bộ payload phù hợp với bối cảnh kiểm thử cụ thể.

> [!NOTE]
> 📷 **Hình 4.1 — Sơ đồ cây thư mục dự án.** Cần chèn ảnh chụp cấu trúc cây thư mục từ IDE hoặc terminal (lệnh `tree`), thể hiện rõ sự phân tách giữa các tầng: `models/`, `routes/`, `services/`, `templates/`.

---

## 4.2. Module Crawler

Module Crawler, được triển khai trong class `CrawlerService` tại tệp `app/services/crawler.py`, đảm nhận bước đầu tiên và quan trọng nhất trong pipeline quét — thu thập bản đồ cấu trúc của ứng dụng web mục tiêu bao gồm danh sách các trang có thể truy cập và các biểu mẫu nhập liệu trên mỗi trang. Chất lượng đầu ra của module này quyết định trực tiếp phạm vi và độ bao phủ của toàn bộ quá trình kiểm thử bảo mật: nếu Crawler bỏ sót một trang chứa biểu mẫu dễ bị tấn công, module Detector sẽ không có cơ hội kiểm tra và lỗ hổng đó sẽ không được phát hiện.

### 4.2.1. Khởi tạo và cấu hình

Khi được khởi tạo, `CrawlerService` nhận năm tham số cấu hình: `base_url` là địa chỉ URL gốc của ứng dụng mục tiêu, `max_depth` (mặc định 3) là giới hạn độ sâu BFS tối đa tính từ trang gốc, `max_pages` (mặc định 50) là giới hạn tổng số trang tối đa sẽ duyệt, `timeout` (mặc định 10 giây) là thời gian chờ tối đa cho mỗi yêu cầu HTTP, và `delay` (mặc định 0.5 giây) là khoảng trễ tối thiểu giữa hai yêu cầu liên tiếp. Constructor thực hiện chuẩn hóa URL đầu vào bằng phương thức tĩnh `_normalize_url()` — đảm bảo URL luôn có scheme (thêm `https://` nếu thiếu) và loại bỏ dấu `/` thừa ở cuối — sau đó trích xuất tên miền cơ sở (`base_domain`) bằng hàm `urlparse` để phục vụ bộ lọc cùng miền trong quá trình duyệt. Ba cấu trúc dữ liệu trạng thái được khởi tạo: tập hợp `visited_urls` (kiểu `set`) lưu các URL đã duyệt để phát hiện trùng lặp với độ phức tạp tra cứu O(1), danh sách `discovered_pages` chứa thông tin chi tiết của từng trang đã phát hiện, và danh sách `discovered_forms` chứa toàn bộ biểu mẫu đã trích xuất. Cuối cùng, một đối tượng `HTTPClient` được tạo để quản lý phiên HTTP với khả năng tự động đăng nhập vào DVWA.

```python
class CrawlerService:
    def __init__(self, base_url, max_depth=3, max_pages=50,
                 timeout=10, delay=0.5):
        self.base_url = self._normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout
        self.delay = delay

        self.visited_urls = set()
        self.discovered_pages = []
        self.discovered_forms = []
        self.http = HTTPClient(timeout=self.timeout)
```

### 4.2.2. Thuật toán BFS duyệt web

Phương thức `crawl()` triển khai thuật toán duyệt theo chiều rộng (BFS — Breadth-First Search) đã được trình bày lý thuyết ở Mục 2.3. Hàng đợi BFS sử dụng cấu trúc `deque` (Double-Ended Queue) từ thư viện chuẩn `collections` của Python, cho phép thao tác thêm phần tử ở cuối (`append`) và lấy phần tử ở đầu (`popleft`) đều có độ phức tạp O(1), phù hợp cho việc mô phỏng hành vi hàng đợi FIFO. Mỗi phần tử trong hàng đợi là một bộ hai giá trị `(url, depth)` ghi nhận cả địa chỉ URL lẫn mức độ sâu hiện tại so với trang gốc.

Trước khi bắt đầu vòng lặp chính, crawler thực hiện một bước xử lý đặc biệt dành cho DVWA: nếu URL mục tiêu chứa chuỗi `login.php`, hệ thống tự động chuyển hướng điểm khởi đầu sang `index.php` để đảm bảo quá trình crawl bắt đầu từ trang chủ thực sự chứa các liên kết đến các module lỗ hổng, thay vì bị kẹt tại trang đăng nhập. Đây là một xử lý thực tế quan trọng vì DVWA yêu cầu xác thực trước khi truy cập bất kỳ trang nào, và `HTTPClient` đã thực hiện bước đăng nhập tự động trong constructor.

Vòng lặp BFS tiếp tục chừng nào hàng đợi còn phần tử và tổng số trang đã duyệt chưa vượt quá `max_pages`. Tại mỗi lượt lặp, một phần tử `(url, depth)` được lấy ra từ đầu hàng đợi. Phần tử bị bỏ qua nếu URL đã nằm trong `visited_urls` (tránh duyệt trùng lặp) hoặc `depth` vượt quá `max_depth` (kiểm soát phạm vi). Nếu hợp lệ, crawler gọi `_fetch_page(url)` để tải nội dung trang thông qua HTTP GET, kiểm tra Content-Type đảm bảo chỉ phân tích trang HTML (bỏ qua ảnh, PDF, JavaScript, CSS), và xây dựng cây DOM bằng BeautifulSoup. Từ cây DOM thu được, crawler đồng thời thực hiện hai thao tác trích xuất: gọi `_extract_forms()` để tìm tất cả biểu mẫu trên trang, và gọi `_extract_links()` để tìm tất cả liên kết nội bộ cùng miền. Các liên kết mới chưa từng duyệt được thêm vào hàng đợi với mức depth tăng thêm một đơn vị. Khoảng trễ `delay` được áp dụng giữa các lần tải trang liên tiếp nhằm tránh gây quá tải cho máy chủ mục tiêu.

```python
def crawl(self):
    # Xử lý đặc biệt cho DVWA
    start_url = self.base_url
    if "login.php" in self.base_url:
        start_url = self.base_url.replace("login.php", "index.php")

    queue = deque([(start_url, 0)])

    while queue and len(self.visited_urls) < self.max_pages:
        url, depth = queue.popleft()

        if url in self.visited_urls or depth > self.max_depth:
            continue

        page_data = self._fetch_page(url)
        if page_data is None:
            continue

        self.visited_urls.add(url)
        self.discovered_pages.append({
            'url': url,
            'depth': depth,
            'status_code': page_data['status_code'],
        })

        forms = self._extract_forms(page_data['soup'], url)
        self.discovered_forms.extend(forms)

        if depth < self.max_depth:
            links = self._extract_links(page_data['soup'], url)
            new_links = links - self.visited_urls
            for link in new_links:
                queue.append((link, depth + 1))

        if self.delay > 0:
            time.sleep(self.delay)

    return {
        'pages': self.discovered_pages,
        'forms': self.discovered_forms,
        'total_pages': len(self.discovered_pages),
        'total_forms': len(self.discovered_forms),
    }
```

### 4.2.3. Trích xuất liên kết và biểu mẫu

Phương thức `_extract_links()` duyệt toàn bộ các thẻ `<a>` có thuộc tính `href` trong cây DOM, chuyển đổi liên kết tương đối thành tuyệt đối bằng hàm `urljoin()`, và lọc bỏ các URL không thuộc cùng miền với mục tiêu. Ngoài ra, phương thức `_should_skip()` loại bỏ các liên kết không phù hợp cho quét bảo mật dựa trên hai tiêu chí: đuôi tệp tĩnh (danh sách `SKIP_EXTENSIONS` bao gồm `.css`, `.js`, `.png`, `.jpg`, `.pdf`, `.zip` và 17 đuôi khác — các tệp này không chứa biểu mẫu nhập liệu nên việc tải và phân tích chúng là lãng phí tài nguyên) và mẫu URL nguy hiểm (danh sách `SKIP_PATTERNS` bao gồm `logout`, `signout`, `mailto:`, `javascript:` — để tránh vô tình kết thúc phiên đăng nhập hoặc theo dõi các liên kết không dẫn đến trang HTML thực sự). Phương thức trả về một tập hợp (`set`) các URL hợp lệ, đã loại bỏ phần fragment (ký tự `#` và nội dung sau nó) để tránh trùng lặp giữa các URL chỉ khác nhau ở phần neo nội trang.

Phương thức `_extract_forms()` duyệt toàn bộ các thẻ `<form>` trong cây DOM và xây dựng một dictionary chứa đầy đủ thông tin cần thiết cho giai đoạn Detection tiếp theo. Đối với mỗi biểu mẫu, crawler trích xuất: `page_url` là URL của trang chứa biểu mẫu (để truy nguyên nguồn gốc), `action` là đường dẫn xử lý biểu mẫu được chuyển thành URL tuyệt đối bằng `urljoin()` (nếu thuộc tính `action` trống thì sử dụng URL của trang hiện tại — hành vi mặc định của trình duyệt), `method` là phương thức HTTP (GET hoặc POST, mặc định GET nếu không chỉ định), và `inputs` là danh sách tất cả các trường nhập liệu (`<input>`, `<textarea>`, `<select>`) với ba thuộc tính `name`, `type` và `value`. Chỉ các trường có thuộc tính `name` mới được thu thập vì các trường không có tên sẽ không được trình duyệt gửi kèm khi submit biểu mẫu.

```python
def _extract_forms(self, soup, page_url):
    forms = []
    for form in soup.find_all('form'):
        action = form.get('action', '')
        form_data = {
            'page_url': page_url,
            'action': urljoin(page_url, action) if action else page_url,
            'method': form.get('method', 'GET').upper(),
            'inputs': [],
        }

        for input_tag in form.find_all(['input', 'textarea', 'select']):
            name = input_tag.get('name', '')
            if not name:
                continue
            input_data = {
                'name': name,
                'type': input_tag.get('type', 'text'),
                'value': input_tag.get('value', ''),
            }
            form_data['inputs'].append(input_data)

        forms.append(form_data)
    return forms
```

### 4.2.4. Xử lý phiên đăng nhập DVWA

Một thách thức kỹ thuật đặc thù khi quét DVWA là ứng dụng này yêu cầu xác thực bắt buộc — toàn bộ các trang chức năng đều chuyển hướng về `login.php` nếu chưa đăng nhập, và biểu mẫu đăng nhập được bảo vệ bằng CSRF token (trường ẩn `user_token`) thay đổi mỗi lần tải trang. Module `HTTPClient` trong tệp `app/utils/http_client.py` giải quyết vấn đề này thông qua cơ chế tự động đăng nhập (Auto-login) ba bước. Bước thứ nhất, client gửi yêu cầu GET đến trang `login.php` để lấy nội dung HTML chứa CSRF token, sau đó sử dụng BeautifulSoup phân tích HTML và trích xuất giá trị `user_token` từ trường `<input>` ẩn có tên `user_token`. Bước thứ hai, client gửi yêu cầu POST đến cùng URL với dữ liệu biểu mẫu bao gồm `username`, `password`, nút `Login` và `user_token` đã trích xuất — các giá trị mặc định (`admin`/`password`) được đọc từ biến môi trường `DVWA_USER` và `DVWA_PASS`, cho phép tùy chỉnh thông tin xác thực mà không cần sửa mã nguồn. Bước thứ ba, sau khi đăng nhập thành công, client thiết lập cookie `security` với giá trị đọc từ biến `DVWA_SECURITY_LEVEL` (mặc định `low`) — cookie này quyết định mức độ bảo vệ của DVWA đối với các cuộc tấn công, ảnh hưởng trực tiếp đến kết quả quét.

```python
def _check_and_login_dvwa(self):
    login_url = os.getenv('DVWA_LOGIN_URL', 'http://dvwa/login.php')
    username = os.getenv('DVWA_USER', 'admin')
    password = os.getenv('DVWA_PASS', 'password')
    security_level = os.getenv('DVWA_SECURITY_LEVEL', 'low').lower()

    # 1. Lấy trang đăng nhập và trích xuất CSRF token
    resp = self.session.get(login_url, timeout=self.timeout)
    soup = BeautifulSoup(resp.text, 'html.parser')
    token_input = soup.find('input', {'name': 'user_token'})
    user_token = token_input.get('value', '') if token_input else ""

    # 2. Gửi yêu cầu đăng nhập với token
    payload = {
        'username': username, 'password': password,
        'Login': 'Login', 'user_token': user_token
    }
    self.session.post(login_url, data=payload, timeout=self.timeout)

    # 3. Thiết lập mức bảo mật
    self.session.cookies.set('security', security_level)
```

Toàn bộ quá trình đăng nhập được bọc trong khối `try-except` để xử lý graceful khi máy chủ DVWA chưa sẵn sàng hoặc không thể kết nối — trong trường hợp đó, crawler vẫn tiếp tục hoạt động nhưng sẽ chỉ có thể truy cập các trang công khai không yêu cầu xác thực. Cookie phiên (`PHPSESSID`) được duy trì tự động bởi đối tượng `requests.Session`, đảm bảo mọi yêu cầu HTTP tiếp theo trong cùng phiên crawl đều mang theo thông tin xác thực đã thiết lập.

> [!NOTE]
> 📷 **Hình 4.2 — Lưu đồ thuật toán BFS crawl.** Cần chèn lưu đồ (Flowchart) mô tả thuật toán crawl: Start → Khởi tạo hàng đợi → Kiểm tra hàng đợi rỗng? → Lấy phần tử → Kiểm tra đã duyệt? → Kiểm tra depth? → Tải trang → Trích xuất forms → Trích xuất links → Thêm vào hàng đợi → Quay lại vòng lặp → Trả về kết quả.

---

## 4.3. Module phát hiện lỗ hổng (Detector)

Module phát hiện lỗ hổng, được triển khai trong class `VulnerabilityDetector` tại tệp `app/services/detector.py`, là thành phần quan trọng nhất của hệ thống — nơi thực hiện kiểm thử bảo mật thực sự bằng cách chèn các payload tấn công vào biểu mẫu và phân tích phản hồi từ máy chủ. Module này triển khai hai bộ phát hiện độc lập cho hai loại lỗ hổng: SQL Injection và Cross-Site Scripting, mỗi bộ áp dụng nhiều chiến lược phân tích song song để tăng độ chính xác và giảm tỉ lệ dương tính giả.

### 4.3.1. Khởi tạo và tải payload

Constructor của `VulnerabilityDetector` thực hiện bốn nhiệm vụ khởi tạo. Đầu tiên, tạo một phiên HTTP riêng (`requests.Session`) với User-Agent tùy chỉnh xác định rõ danh tính công cụ (`AIVulnScanner/1.0`) — đây là thực hành tốt trong kiểm thử bảo mật, cho phép quản trị viên hệ thống mục tiêu phân biệt lưu lượng quét với lưu lượng người dùng thực trong nhật ký truy cập. Tiếp theo, thực hiện bước đăng nhập tự động vào DVWA thông qua phương thức `_login_dvwa()` với cơ chế tương tự như `HTTPClient` đã mô tả ở Mục 4.2.4, đảm bảo detector có phiên xác thực độc lập để gửi payload đến các trang yêu cầu đăng nhập. Sau đó, tải danh sách payload SQL Injection từ tệp `data/payloads/sqli_payloads.txt` và payload XSS từ tệp `data/payloads/xss_payloads.txt` thông qua phương thức tĩnh `_load_payloads()`.

Phương thức `_load_payloads()` đọc tệp payload theo từng dòng, bỏ qua dòng trống và dòng chú thích (bắt đầu bằng `#`), và trả về danh sách các chuỗi payload sẵn sàng sử dụng. Nếu tệp payload không tồn tại (ví dụ khi chạy ngoài thư mục dự án), phương thức tự động sử dụng danh sách payload mặc định được định nghĩa trực tiếp trong mã nguồn dưới dạng thuộc tính class (`SQLI_PAYLOADS` và `XSS_PAYLOADS`), đảm bảo hệ thống luôn hoạt động được ngay cả khi thiếu tệp cấu hình ngoài.

Hệ thống hiện tại sử dụng 10 payload SQL Injection và 10 payload XSS đã được chọn lọc cẩn thận để bao phủ các kỹ thuật tấn công phổ biến nhất. Bộ payload SQLi bao gồm các kỹ thuật: tautology-based (`' OR '1'='1`), comment injection (`' OR 1=1--`), destructive (`'; DROP TABLE users--`), UNION-based (`' UNION SELECT NULL--`), và các biến thể bỏ qua xác thực (`admin'--`, `' OR ''='`). Bộ payload XSS bao gồm: chèn thẻ `<script>` trực tiếp, bypass bằng đóng attribute (`"><script>alert(1)</script>`), sử dụng thẻ `<img>` với event handler (`<img src=x onerror=alert(1)>`), thẻ `<svg>` (`<svg/onload=alert(1)>`), và các biến thể khác như `<body onload>`, `<input autofocus onfocus>`, `<iframe>`.

### 4.3.2. Phát hiện SQL Injection

Quy trình phát hiện SQL Injection cho mỗi biểu mẫu được thực hiện bởi phương thức `test_sqli()` theo bốn giai đoạn chính.

Giai đoạn chuẩn bị bắt đầu bằng việc phân tích cấu trúc biểu mẫu: trích xuất URL đích (`action`), phương thức HTTP (`method`), và xây dựng hai cấu trúc dữ liệu quan trọng — dictionary `default_params` chứa giá trị mặc định cho tất cả trường nhập liệu (sử dụng giá trị `value` có sẵn hoặc chuỗi `'test'` nếu trống), và danh sách `testable_fields` chứa tên các trường có thể kiểm thử (loại trừ các trường thuộc kiểu `submit`, `button`, `image`, `reset`, `file` — được liệt kê trong `SKIP_INPUT_TYPES` — vì các trường này không nhận dữ liệu nhập từ người dùng nên không phải là véc-tơ tấn công tiềm năng).

Giai đoạn thu thập phản hồi cơ sở (Baseline) gọi phương thức `_get_baseline_response()` để gửi một yêu cầu HTTP với dữ liệu biểu mẫu hoàn toàn bình thường (benign) — sử dụng giá trị mặc định hoặc chuỗi `'test'` cho mỗi trường. Phản hồi thu được bao gồm mã trạng thái HTTP (`status_code`), nội dung phản hồi (`content`) và độ dài nội dung (`content_length`), đóng vai trò điểm tham chiếu (Reference Point) để so sánh với các phản hồi khi chèn payload tấn công. Nếu không thể thu thập phản hồi cơ sở (do timeout hoặc lỗi kết nối), biểu mẫu bị bỏ qua vì không có cơ sở để so sánh.

Giai đoạn chèn payload và phân tích duyệt qua từng trường kiểm thử và từng payload SQL Injection theo vòng lặp lồng nhau. Với mỗi cặp `(field, payload)`, detector sao chép dictionary `default_params`, thay thế giá trị của trường đang kiểm thử bằng payload, gửi yêu cầu HTTP đến máy chủ, và so sánh phản hồi thu được với phản hồi cơ sở thông qua phương thức `_compare_responses()`. Phương thức này áp dụng đồng thời ba chiến lược phân tích đã trình bày ở Chương 2.

Chiến lược thứ nhất — phát hiện lỗi SQL (Error-based Detection) — quét nội dung phản hồi HTTP (đã chuyển thành chữ thường) để tìm kiếm sự hiện diện của các chuỗi từ khóa đặc trưng cho thông báo lỗi SQL từ các hệ quản trị cơ sở dữ liệu phổ biến. Danh sách `SQLI_ERROR_PATTERNS` bao gồm 13 mẫu phủ sáu DBMS: MySQL (`'mysql'`, `'mysql_fetch'`, `'warning: mysql'`), SQLite (`'sqlite'`, `'warning: sqlite'`), PostgreSQL (`'postgresql'`, `'pg_query'`, `'warning: pg_'`), Oracle (`'oracle'`), Microsoft SQL Server (`'microsoft sql'`, `'odbc'`), và các mẫu chung (`'sql syntax'`, `'syntax error'`, `'unclosed quotation'`, `'unterminated'`, `'sql error'`, `'database error'`). Khi tìm thấy ít nhất một từ khóa khớp, điểm score được cộng thêm 0.5 — mức trọng số cao nhất trong ba chiến lược — phản ánh độ tin cậy cao của dấu hiệu lỗi SQL hiển thị.

Chiến lược thứ hai — thay đổi mã trạng thái (Status Code Change) — so sánh mã trạng thái HTTP của phản hồi kiểm thử với phản hồi cơ sở. Nếu phát hiện sự khác biệt, score được cộng thêm 0.3 nếu mã trạng thái mới thuộc dải 5xx (lỗi máy chủ — dấu hiệu mạnh cho thấy payload đã gây ra lỗi phía backend), hoặc 0.15 nếu thuộc dải khác (ví dụ chuyển hướng 302, lỗi 403 — dấu hiệu yếu hơn nhưng vẫn đáng chú ý).

Chiến lược thứ ba — bất thường độ dài nội dung (Content Length Anomaly) — tính tỉ lệ chênh lệch giữa độ dài phản hồi kiểm thử và phản hồi cơ sở theo công thức $\Delta = |L_{\text{test}} - L_{\text{baseline}}| / L_{\text{baseline}}$. Nếu tỉ lệ này vượt ngưỡng 30% (hằng số `LENGTH_ANOMALY_THRESHOLD`), score được cộng thêm 0.3. Ngưỡng 30% được chọn dựa trên quan sát thực nghiệm rằng sự thay đổi nhỏ hơn thường do các yếu tố không liên quan đến bảo mật (nội dung động, timestamp, session token hiển thị), trong khi sự thay đổi lớn hơn thường chỉ ra rằng payload đã ảnh hưởng đến logic truy vấn cơ sở dữ liệu — ví dụ điều kiện `OR 1=1` khiến truy vấn trả về toàn bộ bản ghi thay vì chỉ một bản ghi, tạo ra phản hồi dài hơn đáng kể.

```python
def _compare_responses(self, baseline, test_response):
    reasons = []
    score = 0.0

    # Chiến lược 1: Từ khóa lỗi SQL
    body_lower = test_response['content'].lower()
    matched_keywords = [
        kw for kw in self.SQLI_ERROR_PATTERNS if kw in body_lower
    ]
    if matched_keywords:
        reasons.append(
            f"SQL error keyword(s) found: {', '.join(matched_keywords[:3])}"
        )
        score += 0.5

    # Chiến lược 2: Thay đổi mã trạng thái
    if baseline['status_code'] != test_response['status_code']:
        reasons.append(
            f"Status code changed: {baseline['status_code']} → "
            f"{test_response['status_code']}"
        )
        score += 0.3 if test_response['status_code'] >= 500 else 0.15

    # Chiến lược 3: Bất thường độ dài nội dung
    if baseline['content_length'] > 0:
        length_diff = abs(
            test_response['content_length'] - baseline['content_length']
        )
        ratio = length_diff / baseline['content_length']
        if ratio > LENGTH_ANOMALY_THRESHOLD:
            reasons.append(
                f"Content length anomaly: Δ {ratio:.0%}"
            )
            score += 0.3

    score = min(score, 1.0)
    is_suspicious = len(reasons) > 0 and score >= 0.3
    return {
        'is_suspicious': is_suspicious,
        'reasons': reasons,
        'score': score,
    }
```

Giai đoạn xác định mức độ nghiêm trọng sử dụng hai tiêu chí để phân loại finding. Nếu số lượng chiến lược phát hiện đồng thời khớp (tức số phần tử trong danh sách `reasons`) lớn hơn hoặc bằng `HIGH_CONFIDENCE_INDICATORS` (giá trị 2) — nghĩa là có ít nhất hai chiến lược độc lập cùng xác nhận dấu hiệu bất thường — hoặc nếu tổng điểm `score` lớn hơn hoặc bằng 0.5, lỗ hổng được phân loại mức `high`. Trong trường hợp còn lại (chỉ một chiến lược phát hiện với điểm thấp hơn), lỗ hổng được phân loại mức `medium`. Khi phát hiện lỗ hổng trên một trường nhập liệu, vòng lặp payload cho trường đó ngay lập tức kết thúc bằng lệnh `break` — đây là chiến lược tối ưu hóa hiệu năng quan trọng: một khi đã xác nhận trường dễ bị tấn công bằng payload đầu tiên, việc thử các payload còn lại trên cùng trường là không cần thiết và chỉ làm tăng thời gian quét.

### 4.3.3. Phát hiện Cross-Site Scripting (XSS)

Phương thức `test_xss()` thực hiện quy trình tương tự `test_sqli()` về mặt cấu trúc vòng lặp — duyệt qua từng trường kiểm thử và từng payload XSS, chèn payload vào biểu mẫu và gửi yêu cầu HTTP — nhưng sử dụng phương thức phân tích phản hồi khác biệt hoàn toàn thông qua `_check_xss_reflection()`. Điểm khác biệt cốt lõi so với SQLi là detector XSS không cần thu thập phản hồi cơ sở để so sánh, vì tiêu chí phát hiện dựa trên sự hiện diện trực tiếp của payload trong phản hồi chứ không dựa trên sự thay đổi hành vi so với phản hồi bình thường.

Phương thức `_check_xss_reflection()` áp dụng ba chiến lược phân tích song song, trong đó hai chiến lược sau chỉ được tính điểm khi chiến lược đầu tiên đã phát hiện dấu hiệu — thiết kế có chủ đích này giúp giảm đáng kể tỉ lệ dương tính giả.

Chiến lược thứ nhất — phát hiện phản xạ payload (Reflected Payload Detection) — kiểm tra xem toàn bộ chuỗi payload gốc có xuất hiện nguyên vẹn (case-insensitive) trong nội dung phản hồi HTML hay không. Đây là dấu hiệu mạnh nhất cho thấy máy chủ đã nhận dữ liệu đầu vào từ người dùng và chèn trực tiếp vào trang phản hồi mà không thực hiện mã hóa (Encoding) hoặc lọc (Sanitization). Tuy nhiên, trước khi kết luận, chiến lược này thực hiện một bước kiểm tra quan trọng: xác minh payload không bị mã hóa HTML. Cụ thể, phương thức duyệt danh sách `XSS_ENCODED_PATTERNS` (bao gồm `&lt;script`, `&lt;img`, `&lt;svg`, `&lt;iframe`, `&amp;lt;`, `&#60;`, `&#x3c;`) và nếu tìm thấy bất kỳ mẫu nào, kết luận rằng máy chủ đã thực hiện HTML Output Encoding đúng cách — payload tuy xuất hiện trong phản hồi nhưng ở dạng đã mã hóa an toàn (ví dụ `<` thành `&lt;`), trình duyệt sẽ hiển thị nó dưới dạng văn bản thuần chứ không thực thi như mã JavaScript. Nếu payload xuất hiện nguyên vẹn và không bị mã hóa, score được cộng 0.6.

Chiến lược thứ hai — phát hiện event handler (Event Handler Detection) — tìm kiếm sự hiện diện của các thuộc tính JavaScript nguy hiểm trong phản hồi, bao gồm `onerror=`, `onload=`, `onfocus=`, `onclick=`, `onmouseover=`, `onsubmit=`, `onchange=`. Chiến lược này chỉ cộng điểm (0.2) khi chiến lược đầu tiên đã phát hiện dấu hiệu (tức `score > 0`), tránh trường hợp các event handler có sẵn trong mã HTML gốc của ứng dụng (không phải do injection) bị đánh dấu nhầm là lỗ hổng.

Chiến lược thứ ba — phát hiện thẻ nguy hiểm (Dangerous Tag Detection) — tìm kiếm sự hiện diện của các thẻ HTML có khả năng thực thi mã trong phản hồi, bao gồm `<script`, `<iframe`, `<object`, `<embed`, `<svg`, `<img src=x`, `<body`. Tương tự chiến lược thứ hai, điểm (0.2) chỉ được cộng khi đã có dấu hiệu phản xạ từ chiến lược đầu tiên.

```python
def _check_xss_reflection(self, payload, response_content):
    reasons = []
    score = 0.0
    content_lower = response_content.lower()
    payload_lower = payload.lower()

    # Chiến lược 1: Phản xạ payload nguyên vẹn
    if payload_lower in content_lower:
        is_encoded = any(
            enc in content_lower
            for enc in self.XSS_ENCODED_PATTERNS
        )
        if not is_encoded:
            reasons.append(
                f"Reflected payload found: {payload[:40]}"
            )
            score += 0.6

    # Chiến lược 2: Event handler (chỉ khi đã có dấu hiệu phản xạ)
    matched_handlers = [
        h for h in self.XSS_EVENT_HANDLERS if h in content_lower
    ]
    if matched_handlers and score > 0:
        reasons.append(
            f"Event handler(s) detected: {', '.join(matched_handlers[:3])}"
        )
        score += 0.2

    # Chiến lược 3: Thẻ nguy hiểm (chỉ khi đã có dấu hiệu phản xạ)
    matched_tags = [
        tag for tag in self.XSS_DANGEROUS_TAGS if tag in content_lower
    ]
    if matched_tags and score > 0:
        reasons.append(
            f"Dangerous tag(s): {', '.join(matched_tags[:3])}"
        )
        score += 0.2

    score = min(score, 1.0)
    is_reflected = score >= 0.5
    return {
        'is_reflected': is_reflected,
        'reasons': reasons,
        'score': score,
    }
```

Mức severity của XSS được xác định theo ba ngưỡng: `high` nếu `score >= 0.8` (payload phản xạ kèm cả event handler và thẻ nguy hiểm — xác nhận rõ ràng khả năng thực thi mã), `medium` nếu `score >= 0.5` (payload phản xạ nhưng chỉ có một trong hai dấu hiệu phụ), và `low` cho các trường hợp còn lại.

Mỗi lỗ hổng phát hiện được đóng gói thành một dictionary (finding) chứa đầy đủ thông tin: `vuln_type` (giá trị `'sqli'` hoặc `'xss'`), `severity`, `url` (địa chỉ biểu mẫu bị ảnh hưởng), `parameter` (tên trường dễ bị tấn công), `payload` (chuỗi payload cụ thể đã kích hoạt), `evidence` (bằng chứng — chuỗi nối các `reasons` bằng dấu chấm phẩy), `method` (GET hoặc POST), `score` (điểm tin cậy) và `response_data` (dữ liệu phản hồi thô cho phân tích AI). Dictionary này được thêm vào cả danh sách `form_findings` (trả về cho phiên quét hiện tại) lẫn danh sách `self.findings` (lưu trữ tích lũy toàn bộ findings qua nhiều biểu mẫu).

> [!NOTE]
> 📷 **Hình 4.3 — Lưu đồ thuật toán phát hiện SQL Injection.** Cần chèn lưu đồ mô tả quy trình: Nhận form → Xây dựng default_params → Thu thập baseline → Vòng lặp (field × payload) → Chèn payload → Gửi request → Phân tích 3 chiến lược → Tính score → Xác định severity → Lưu finding.

> [!NOTE]
> 📷 **Hình 4.4 — Lưu đồ thuật toán phát hiện XSS.** Cần chèn lưu đồ tương tự Hình 4.3 nhưng cho XSS: Nhận form → Vòng lặp (field × payload) → Chèn payload → Gửi request → Kiểm tra phản xạ → Kiểm tra mã hóa HTML → Kiểm tra event handler → Kiểm tra thẻ nguy hiểm → Tính score → Lưu finding.

---

## 4.4. Module AI Advisor

Module AI Advisor, được triển khai trong class `AIAdvisor` tại tệp `app/services/ai_advisor.py`, đảm nhận vai trò trợ lý bảo mật thông minh của hệ thống — phân tích từng lỗ hổng đã phát hiện, giải thích nguyên nhân gốc rễ, đánh giá tác động tiềm tàng, và đề xuất các bước khắc phục cụ thể kèm mã nguồn minh họa. Đây là thành phần tạo nên sự khác biệt cốt lõi của hệ thống so với các công cụ scanner truyền thống — thay vì chỉ liệt kê danh sách lỗ hổng khô khan, hệ thống cung cấp lời khuyên hành động cụ thể và dễ hiểu cho từng trường hợp.

### 4.4.1. Kiến trúc đa nhà cung cấp (Multi-Provider)

`AIAdvisor` được thiết kế với khả năng hỗ trợ đồng thời nhiều nhà cung cấp dịch vụ mô hình ngôn ngữ lớn (LLM). Khi khởi tạo, constructor nhận hai tham số: `provider` xác định nhà cung cấp cần sử dụng (giá trị `'gemini'` cho Google Gemini hoặc `'blackbox'` cho Blackbox AI, mặc định đọc từ biến môi trường `AI_PROVIDER`) và `api_key` là khóa API tương ứng (mặc định đọc từ `GEMINI_API_KEY` hoặc `BLACKBOX_API_KEY`). Tùy theo nhà cung cấp được chọn, constructor thực hiện khởi tạo khác nhau: đối với Gemini, cấu hình SDK chính thức `google-generativeai` bằng lệnh `genai.configure(api_key=...)` và tạo đối tượng `GenerativeModel('gemini-flash-latest')` — sử dụng phiên bản mới nhất của dòng Gemini Flash tối ưu cho tốc độ phản hồi; đối với Blackbox, lưu trữ URL endpoint API (`https://api.blackbox.ai/v1/chat/completions`) để gửi yêu cầu REST trực tiếp.

Phương thức `is_available()` kiểm tra tính sẵn sàng của dịch vụ AI bằng cách xác minh API key không rỗng và không chứa giá trị mặc định mẫu (`your_gemini_api_key`). Phương thức `get_model_name()` trả về tên hiển thị thân thiện của mô hình đang sử dụng — `"Google Gemini (Latest)"` hoặc `"Blackbox (DeepSeek-V3)"` — phục vụ hiển thị trên giao diện sidebar.

```python
class AIAdvisor:
    def __init__(self, provider=None, api_key=None):
        self.provider = provider or os.getenv('AI_PROVIDER', 'blackbox').lower()

        if self.provider == 'gemini':
            self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.api_key = api_key or os.getenv('BLACKBOX_API_KEY', '')
            self.api_url = "https://api.blackbox.ai/v1/chat/completions"
```

### 4.4.2. Thiết kế Prompt cho phân tích bảo mật

Phương thức `_build_remediation_prompt()` xây dựng prompt chuyên biệt cho việc phân tích lỗ hổng bảo mật. Prompt được thiết kế theo cấu trúc có chủ đích rõ ràng, bao gồm ba phần: phần mở đầu xác định vai trò và nhiệm vụ cụ thể của LLM (`"Analyze this [SQL Injection/XSS] finding"`), phần ngữ cảnh cung cấp đầy đủ thông tin kỹ thuật về lỗ hổng (URL bị ảnh hưởng, tên tham số, payload đã sử dụng), và phần chỉ dẫn đầu ra yêu cầu LLM trả về kết quả dưới dạng JSON với ba trường bắt buộc: `explanation` (giải thích lỗ hổng), `remediation_steps` (danh sách bước khắc phục), và `code_example` (mã nguồn an toàn minh họa).

Việc yêu cầu LLM trả về JSON chuẩn hóa thay vì văn bản tự do mang lại hai lợi ích quan trọng: thứ nhất, kết quả có thể được phân tích tự động bằng chương trình (`json.loads()`) và lưu trữ riêng biệt vào các trường tương ứng trong bảng `ai_results`, thay vì lưu toàn bộ thành một đoạn văn bản dài; thứ hai, mỗi phần nội dung (giải thích, bước khắc phục, mã ví dụ) có thể được hiển thị riêng biệt trên giao diện với định dạng và biểu tượng phù hợp, tạo trải nghiệm đọc tốt hơn. Đối với Gemini, prompt còn được hỗ trợ bởi tham số `generation_config` với `response_mime_type: "application/json"`, hướng dẫn mô hình sinh đầu ra đúng định dạng JSON ngay từ mức SDK.

```python
def _build_remediation_prompt(self, vuln_type, severity,
                               url, parameter, payload, evidence):
    vuln_label = 'SQL Injection' if vuln_type == 'sqli' else 'XSS'
    return f"""Analyze this {vuln_label} finding and respond with JSON only:
URL: {url}
Parameter: {parameter}
Payload: {payload}

JSON format:
{{
  "explanation": "Brief explanation",
  "remediation_steps": ["Step 1", "Step 2"],
  "code_example": "Code snippet"
}}"""
```

### 4.4.3. Gọi API và xử lý phản hồi

Phương thức trung tâm `_ask_ai()` điều phối toàn bộ quá trình giao tiếp với LLM. Trước khi gọi API, phương thức kiểm tra tính sẵn sàng thông qua `is_available()`; nếu API key thiếu hoặc không hợp lệ, trả về thông báo lỗi mô tả rõ nguyên nhân thay vì để hệ thống gặp lỗi runtime. Tùy theo nhà cung cấp đã cấu hình, phương thức chuyển hướng đến một trong hai phương thức chuyên biệt.

Phương thức `_call_gemini_sdk()` sử dụng SDK chính thức `google-generativeai` để giao tiếp với Google Gemini. Cuộc gọi API được thực hiện thông qua phương thức `model.generate_content(prompt, generation_config=...)`, trong đó `generation_config` chứa `response_mime_type: "application/json"` khi yêu cầu đầu ra dạng JSON. SDK xử lý tự động các chi tiết giao thức HTTP, mã hóa/giải mã request/response, và quản lý xác thực API key.

Phương thức `_call_blackbox()` giao tiếp với Blackbox AI qua REST API chuẩn OpenAI-compatible. Yêu cầu HTTP POST được gửi đến endpoint với body JSON chứa danh sách messages (một message duy nhất role `user` với nội dung là prompt), tên mô hình (`blackboxai/x-ai/grok-code-fast-1:free`), giới hạn token đầu ra (`max_tokens: 1024`), và chế độ streaming tắt (`stream: false`). Phản hồi từ Blackbox có thể ở dạng JSON chuẩn hoặc Server-Sent Events (SSE), vì vậy phương thức `_parse_blackbox_response()` xử lý cả hai trường hợp: nếu phản hồi chứa tiền tố `"data: "`, duyệt từng dòng tìm dòng chứa `"choices"` và phân tích JSON; ngược lại, phân tích toàn bộ phản hồi như JSON chuẩn.

Phương thức `_process_content()` thực hiện hậu xử lý nội dung phản hồi từ LLM. Khi yêu cầu đầu ra JSON (`is_json=True`), phương thức áp dụng thuật toán phân tích JSON linh hoạt (Robust JSON Recovery) để xử lý các trường hợp LLM trả về JSON không hoàn hảo: trước tiên thử trích xuất chuỗi JSON từ phản hồi bằng biểu thức chính quy `r'\{.*\}'` (tìm khối nội dung nằm giữa cặp dấu ngoặc nhọn ngoài cùng, bao gồm cả nội dung lồng nhau nhờ cờ `re.DOTALL` cho phép dấu chấm khớp ký tự xuống dòng), rồi phân tích bằng `json.loads()`; nếu thất bại, thử phân tích toàn bộ nội dung như JSON; nếu vẫn thất bại, trả về dictionary mặc định với toàn bộ nội dung phản hồi đặt trong trường `explanation` — đảm bảo hệ thống không bao giờ mất thông tin từ LLM ngay cả khi định dạng đầu ra không đúng kỳ vọng.

### 4.4.4. Tính năng Chat Q&A

Ngoài phân tích tự động trong pipeline quét, `AIAdvisor` cung cấp tính năng hỏi đáp tương tác thông qua phương thức `ask_question()`. Phương thức này nhận hai tham số: `question` là câu hỏi bằng ngôn ngữ tự nhiên của người dùng, và `finding_context` (tùy chọn) là dictionary chứa ngữ cảnh lỗ hổng đang được thảo luận. Khi có ngữ cảnh, phương thức xây dựng khối thông tin bối cảnh (`"THE CONTEXT:"`) bao gồm loại lỗ hổng, URL, tham số và payload, rồi nhúng khối này vào prompt trước câu hỏi. Prompt được thiết kế với chỉ dẫn rõ ràng cho LLM: đóng vai trò Security Consultant, trả lời trực tiếp và cụ thể dựa trên ngữ cảnh, sử dụng ngôn ngữ kỹ thuật nhưng dễ hiểu, và trả lời bằng ngôn ngữ của câu hỏi (hỗ trợ đa ngôn ngữ). Kết quả trả về là chuỗi văn bản (không phải JSON) vì nội dung hỏi đáp tự do không cần cấu trúc cứng nhắc.

Tại tầng Controller, Blueprint `ai_chat_bp` trong tệp `app/routes/ai_chat.py` xử lý endpoint `POST /ai/ask`. Route handler nhận JSON request chứa `question` và `vulnerability_id` (tùy chọn), xây dựng `finding_context` từ bản ghi `Vulnerability` trong cơ sở dữ liệu nếu có `vulnerability_id`, gọi `advisor.ask_question()`, và trả về JSON response chứa `answer`. Quan trọng hơn, route handler thực hiện lưu trữ lâu dài cho cả hai phía hội thoại: trước khi gọi AI, lưu tin nhắn người dùng dưới dạng `ChatMessage(role='user')`, sau khi nhận phản hồi, lưu câu trả lời dưới dạng `ChatMessage(role='assistant')` — cả hai đều liên kết với `vulnerability_id` tương ứng. Cơ chế lưu trữ này cho phép khôi phục toàn bộ lịch sử hội thoại khi người dùng quay lại xem kết quả quét sau này.

> [!NOTE]
> 📷 **Hình 4.5 — Sơ đồ luồng xử lý AI Advisor.** Cần chèn sơ đồ mô tả hai luồng: (1) Luồng phân tích tự động: Finding → Build prompt → Call Gemini/Blackbox → Parse JSON → Save AIResult; (2) Luồng Chat Q&A: User question + Vulnerability context → Build prompt → Call LLM → Return answer + Save ChatMessage.

---

## 4.5. Module Scanner Engine (Bộ điều phối)

Module Scanner Engine, được triển khai trong class `ScannerEngine` tại tệp `app/services/scanner.py`, đóng vai trò bộ điều phối trung tâm (Orchestrator) quản lý toàn bộ pipeline quét từ đầu đến cuối. Thay vì triển khai logic nghiệp vụ trực tiếp, Scanner Engine ủy thác từng bước xử lý cho các module chuyên biệt — CrawlerService, VulnerabilityDetector, AIAdvisor — đồng thời quản lý trạng thái phiên quét, lưu trữ kết quả trung gian vào cơ sở dữ liệu sau mỗi bước, và xử lý lỗi toàn cục. Mẫu thiết kế này tuân thủ nguyên tắc Single Responsibility: Scanner Engine chỉ biết thứ tự các bước cần thực hiện và cách kết nối đầu ra của bước trước với đầu vào của bước sau, không biết chi tiết thuật toán BFS, chiến lược phát hiện lỗ hổng hay cách giao tiếp với API AI.

### 4.5.1. Orchestration Pipeline

Constructor của `ScannerEngine` nhận ba tham số: `target_url` là URL mục tiêu cần quét, `scan_config` là dictionary chứa tham số cấu hình (bao gồm `crawl_depth`, `test_sqli`, `test_xss`, `use_ai`, `max_pages`, `timeout`), và `user_id` là ID người dùng đang thực hiện quét (bắt buộc, phục vụ phân quyền dữ liệu). Phương thức trung tâm `run()` thực thi pipeline gồm bảy bước tuần tự, tất cả được bọc trong khối `try-except` cấp cao nhất.

Bước 0 (`_create_scan_record`) tạo bản ghi `Scan` mới trong cơ sở dữ liệu với `status='running'` và `started_at` bằng thời điểm UTC hiện tại, gọi `db.session.commit()` để lưu và nhận `scan.id` tự động tăng — ID này được sử dụng làm khóa ngoại cho tất cả các bản ghi con tạo trong các bước tiếp theo.

Bước 1 (`_run_crawler`) khởi tạo `CrawlerService` với tham số `crawl_depth` và `max_pages` từ cấu hình, gọi `crawler.crawl()` và nhận kết quả dưới dạng dictionary chứa danh sách `pages` và `forms`. Bước 2 (`_save_pages`) duyệt danh sách trang, đếm số biểu mẫu trên mỗi trang bằng cách lọc danh sách `forms` theo `page_url`, tạo bản ghi `Page` cho mỗi trang kèm thông tin `url`, `status_code`, `depth`, `has_forms`, `form_count`, và commit vào cơ sở dữ liệu.

Bước 3 (`_run_detection`) là bước tốn thời gian nhất trong pipeline. Phương thức kiểm tra hai cờ cấu hình `test_sqli` và `test_xss` để xác định loại kiểm thử được bật (cả hai đều bật theo mặc định). Nếu không có loại nào được bật hoặc không tìm thấy biểu mẫu nào trong giai đoạn crawl, bước này trả về danh sách rỗng. Ngược lại, phương thức khởi tạo `VulnerabilityDetector` và duyệt qua từng biểu mẫu, lần lượt gọi `detector.test_sqli(form)` và/hoặc `detector.test_xss(form)`, gộp tất cả findings vào danh sách `all_findings`.

```python
def run(self):
    try:
        self._create_scan_record()
        crawl_results = self._run_crawler()
        self._save_pages(crawl_results)

        findings = self._run_detection(crawl_results)
        saved_vulns = []
        if findings:
            saved_vulns = self._save_vulnerabilities(findings)

        if self.config.get('use_ai', True) and saved_vulns:
            self._run_ai_remediation(findings, saved_vulns)

        self._finalize_scan(crawl_results, len(findings))
        return self.scan

    except Exception as exc:
        logger.error("Scan failed for %s: %s", self.target_url, exc)
        self._mark_failed(str(exc))
        raise
```

Bước 4 (`_save_vulnerabilities`) tạo bản ghi `Vulnerability` cho mỗi finding, gán các thuộc tính từ dictionary finding (`vuln_type`, `severity`, `url`, `parameter`, `payload`, `evidence`), commit vào cơ sở dữ liệu, và trả về danh sách đối tượng ORM đã lưu — quan trọng là các đối tượng này đã có `id` được gán tự động bởi SQLAlchemy sau khi commit, phục vụ việc liên kết khóa ngoại ở bước tiếp theo.

Bước 5 (`_run_ai_remediation`) chỉ thực thi nếu cấu hình `use_ai` được bật và có ít nhất một lỗ hổng đã lưu. Phương thức khởi tạo `AIAdvisor`, duyệt song song danh sách `findings` và `saved_vulns` bằng hàm `zip()`, gọi `advisor.get_remediation()` cho mỗi cặp để nhận phân tích AI dưới dạng dictionary JSON, tạo bản ghi `AIResult` liên kết với `vulnerability_id` tương ứng, và commit toàn bộ vào cơ sở dữ liệu. Trường `remediation` trong `AIResult` lưu danh sách bước khắc phục dưới dạng chuỗi JSON (thông qua `json.dumps()`) để hỗ trợ lưu trữ mảng trong trường Text đơn giản của SQLite.

Bước cuối (`_finalize_scan`) cập nhật bản ghi `Scan` với trạng thái `'completed'`, thời điểm hoàn thành `completed_at`, và ba thống kê tổng hợp: `total_pages`, `total_forms`, `total_vulnerabilities` — ba giá trị này được lưu trực tiếp trong bản ghi Scan thay vì tính toán lại mỗi khi truy vấn, tối ưu hiệu năng hiển thị trên giao diện lịch sử và kết quả.

### 4.5.2. Xử lý lỗi và Fallback

Cơ chế xử lý lỗi của Scanner Engine được thiết kế theo nguyên tắc "fail gracefully": nếu bất kỳ bước nào trong pipeline ném biệt lệ (Exception), khối `except` cấp cao nhất trong `run()` thực hiện hai hành động — gọi `_mark_failed(str(exc))` để cập nhật trạng thái `Scan` thành `'failed'` kèm thời điểm hoàn thành, và re-raise exception lên tầng Controller để Controller xử lý hiển thị lỗi cho người dùng. Phương thức `_mark_failed()` bao gồm bước kiểm tra phòng thủ `if self.scan and self.scan.id` để xử lý trường hợp lỗi xảy ra ngay ở bước tạo bản ghi (khi `self.scan` chưa được gán).

Tại tầng Controller (tệp `app/routes/scan.py`), route handler `new_scan()` bắt exception từ `engine.run()`, tạo flash message lỗi chứa thông tin exception (ví dụ `"Scan failed for http://target: Connection refused"`), và render lại trang `scan.html` với thông báo lỗi — cho phép người dùng xem nguyên nhân lỗi, chỉnh sửa cấu hình nếu cần, và thử lại mà không mất ngữ cảnh nhập liệu.

> [!NOTE]
> 📷 **Hình 4.6 — Sơ đồ pipeline Scanner Engine.** Cần chèn sơ đồ luồng thể hiện bảy bước tuần tự: Create Scan → Crawl → Save Pages → Detect Vulns → Save Vulns → AI Remediation → Finalize, với nhánh rẽ lỗi từ mỗi bước đến _mark_failed().

---

## 4.6. Giao diện người dùng

Giao diện người dùng của hệ thống được xây dựng trên nền tảng template engine Jinja2 tích hợp sẵn trong Flask, kết hợp CSS tùy chỉnh theo phong cách Glassmorphism và JavaScript phía client cho các tương tác động không tải lại trang. Toàn bộ chín template HTML trong thư mục `templates/` đều kế thừa từ template cơ sở `base.html` thông qua cơ chế Template Inheritance của Jinja2, đảm bảo tính nhất quán về bố cục, định kiểu và hành vi trên toàn bộ hệ thống.

### 4.6.1. Trang cấu hình quét (scan.html)

Trang cấu hình quét (`scan.html`) là giao diện trung tâm mà người dùng tương tác nhiều nhất, được thiết kế theo bố cục hai cột: cột chính bên trái chứa biểu mẫu cấu hình, cột phụ bên phải chứa thông tin bổ sung và lưu ý sử dụng.

Biểu mẫu cấu hình bao gồm ba nhóm tùy chọn được tổ chức trong các panel glassmorphism (class `premium-panel`). Nhóm đầu tiên là trường nhập URL mục tiêu — sử dụng ô nhập kiểu URL với icon quả cầu (`globe`) và hiệu ứng focus phát sáng (glow): khi người dùng nhấn vào trường nhập, viền chuyển màu sang accent (`#6366f1`) kèm vùng phát sáng mờ (`box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15)`), tạo cảm giác phản hồi tức thì cho hành động. Nhóm thứ hai là bộ chọn độ sâu crawl — sử dụng custom dropdown thay thế thẻ `<select>` mặc định của trình duyệt, với ba lựa chọn: "1 — surface only" cho quét nhanh chỉ trang gốc, "2 — balanced" (mặc định) cho cân bằng giữa phạm vi và thời gian, "3 — exhaustive" cho quét toàn diện nhất. Nhóm thứ ba gồm ba feature card — mỗi card tương ứng một module kiểm thử (SQL Injection, XSS, AI Remediation). Mỗi feature card được thiết kế dưới dạng label chứa checkbox ẩn, icon minh họa, tiêu đề, mô tả ngắn và ô kiểm tròn; khi checkbox được chọn, card chuyển sang trạng thái active với viền accent, nền tím nhạt và icon phát sáng gradient — tất cả thông qua pseudo-class CSS `:has(input:checked)` mà không cần JavaScript, tận dụng CSS hiện đại để giảm thiểu mã script.

Khi người dùng nhấn nút "Launch Scan" (nút gradient với hiệu ứng hover nâng lên `translateY(-2px)` kèm bóng đổ mở rộng), JavaScript phía client ẩn biểu mẫu cấu hình và hiển thị panel tiến trình quét (`scan-progress-panel`) tại vị trí cùng vùng nội dung. Panel tiến trình bao gồm bốn thành phần trực quan: biểu tượng lá chắn (Shield) xoay và phát sáng nhịp nhàng sử dụng ba animation CSS lồng nhau (ring xoay `shieldSpin`, core phóng to/thu nhỏ `shieldPulse`, icon lật 3D `shieldIconFlip`); thanh tiến trình gradient với hiệu ứng shimmer mô phỏng ánh sáng di chuyển; bốn bước pipeline (Crawling, SQL Injection, XSS, AI Classification) hiển thị dưới dạng danh sách với trạng thái chuyển đổi từ chờ (mờ, icon tĩnh) sang đang xử lý (sáng, viền accent, icon animation riêng cho mỗi bước — globe xoay cho crawl, database nhồi cho SQLi, code nhấp nháy cho XSS, CPU phóng to cho AI) sang hoàn thành (icon check xanh); và bộ đếm thời gian (elapsed timer) cập nhật mỗi giây ở định dạng `MM:SS`. Tiến trình được mô phỏng (simulated) bằng JavaScript vì quá trình quét diễn ra đồng bộ trên server — form được submit bình thường dưới dạng HTTP POST, và khi server phản hồi (redirect đến trang kết quả hoặc render lại trang với lỗi), trang tự động tải lại.

> [!NOTE]
> 📷 **Hình 4.7 — Ảnh chụp trang cấu hình quét (scan.html).** Cần chèn screenshot cho hai trạng thái: (a) Giao diện cấu hình với biểu mẫu nhập URL, feature cards và nút Launch Scan; (b) Giao diện tiến trình quét với shield animation, thanh tiến trình và pipeline steps.

### 4.6.2. Trang kết quả quét (results.html)

Trang kết quả (`results.html`) hiển thị toàn bộ thông tin của một phiên quét đã hoàn thành, được tổ chức theo cấu trúc phân cấp từ tổng quan đến chi tiết. Phần đầu trang gồm dải thống kê (stat strip) hiển thị bốn chỉ số quan trọng trên một hàng ngang: số trang đã duyệt (Pages crawled), số biểu mẫu phát hiện (Forms found), số lỗ hổng (Findings — với chữ số đổi sang màu đỏ nếu lớn hơn 0), và số khuyến nghị AI (AI Remediation — chỉ hiển thị khi có).

Phần chính hiển thị danh sách lỗ hổng dưới dạng các thẻ mở rộng (expandable cards) sử dụng cặp thẻ HTML5 `<details>/<summary>`. Mỗi thẻ ở trạng thái thu gọn hiển thị một dòng tóm tắt gồm: biểu tượng chevron xoay khi mở rộng, badge mức severity với mã màu (đỏ cho HIGH, cam cho MEDIUM, vàng cho LOW), badge loại lỗ hổng (SQLi hoặc XSS), URL bị ảnh hưởng và tên tham số hiển thị bằng phông monospace, và tag "AI Fix Available" nếu có phân tích AI. Khi người dùng nhấn vào thẻ, phần chi tiết mở rộng hiển thị bốn khối thông tin: Endpoint (URL đầy đủ trong khối code), Vulnerable parameter (tên tham số), Payload (chuỗi payload đã sử dụng), và Evidence (bằng chứng phát hiện).

Nếu lỗ hổng có phân tích AI đính kèm, khối AI Remediation hiển thị thêm ba phần nội dung với icon và nhãn màu riêng biệt: "Why?" (icon cảnh báo vàng) chứa giải thích nguyên nhân, "How to fix" (icon check xanh) chứa danh sách bước khắc phục được đánh số thứ tự bằng thẻ `<ol>`, và "Code example" (icon code tím) chứa đoạn mã nguồn an toàn trong khối `<pre>`. Cuối cùng, nút "Chat with AI Advisor" cho phép mở panel hỏi đáp ngay bên dưới — panel này chứa vùng hiển thị tin nhắn (scrollable, hiển thị lịch sử hội thoại đã lưu từ bảng `chat_messages`), ô nhập tin nhắn và nút gửi. Khi nhấn Enter hoặc nút gửi, JavaScript gọi hàm `sendAIQuestion()` thực hiện yêu cầu AJAX (`fetch('/ai/ask')`) với body JSON chứa câu hỏi và `vulnerability_id`, nhận phản hồi và hiển thị tin nhắn AI mới mà không tải lại trang.

```javascript
function sendAIQuestion(vulnId) {
  const input = document.getElementById('ai-input-' + vulnId);
  const messages = document.getElementById('ai-messages-' + vulnId);
  const question = input.value.trim();
  if (!question) return;

  // Hiển thị tin nhắn người dùng
  // ... (tạo DOM element cho user message)

  // Hiển thị trạng thái loading
  const loadingMsg = document.createElement('div');
  loadingMsg.textContent = 'AI is thinking...';
  messages.appendChild(loadingMsg);

  fetch('/ai/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      vulnerability_id: vulnId
    })
  })
  .then(r => r.json())
  .then(data => {
    loadingMsg.remove();
    // Hiển thị câu trả lời AI
    // ... (tạo DOM element cho AI message)
    messages.scrollTop = messages.scrollHeight;
  });
}
```

> [!NOTE]
> 📷 **Hình 4.8 — Ảnh chụp trang kết quả quét (results.html).** Cần chèn screenshot cho ba trạng thái: (a) Trang kết quả tổng quan với stat strip và danh sách lỗ hổng thu gọn; (b) Một finding đã mở rộng hiển thị chi tiết kỹ thuật và phân tích AI; (c) Panel Chat AI đang hoạt động với lịch sử hội thoại.

### 4.6.3. Trang lịch sử quét (history.html)

Trang lịch sử (`history.html`) liệt kê tất cả các phiên quét mà người dùng đã thực hiện, sắp xếp theo thời gian giảm dần (phiên mới nhất hiển thị đầu tiên). Mỗi phiên quét được hiển thị dưới dạng một dòng trong danh sách card, chứa: URL mục tiêu (phông monospace, có tooltip hiển thị URL đầy đủ khi hover), badge trạng thái với mã màu (xanh cho completed, đỏ cho failed, vàng cho running/pending), thời điểm bắt đầu, số lỗ hổng phát hiện (nếu hoàn thành), và nút "View Results" dẫn đến trang kết quả chi tiết tương ứng thông qua `url_for('results.show_results', scan_id=scan.id)`. Khi không có phiên quét nào, giao diện hiển thị trạng thái rỗng (Empty State) với icon minh họa, thông điệp hướng dẫn và nút Call-to-Action dẫn đến trang cấu hình quét mới. Truy vấn dữ liệu chỉ lấy các phiên quét thuộc sở hữu của người dùng hiện tại thông qua điều kiện `Scan.user_id == current_user.id`, đảm bảo tính riêng tư dữ liệu giữa các tài khoản.

### 4.6.4. Hiệu ứng hoạt ảnh (Loading Animation)

Hệ thống sử dụng CSS animations để tạo các hiệu ứng trực quan phản ánh trạng thái hoạt động, giúp người dùng nhận biết hệ thống đang xử lý và không bị nhầm lẫn rằng ứng dụng bị treo. Hiệu ứng chính trên trang cấu hình quét bao gồm: vòng xoay bao quanh biểu tượng lá chắn sử dụng `border-top-color` trên phần tử tròn kết hợp `animation: shieldSpin 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite` — đường cong cubic-bezier tạo hiệu ứng tăng tốc–giảm tốc mượt mà thay vì xoay đều đơn điệu; lõi lá chắn phóng to/thu nhỏ nhẹ (`scale(1) → scale(1.05)`) mỗi 2 giây tạo nhịp thở sống động; icon bên trong lật 3D quanh trục Y (`rotateY(0deg → 360deg)`) mỗi 3 giây với hiệu ứng perspective tạo cảm giác chiều sâu. Mỗi bước trong pipeline có animation riêng biệt khi đang active: globe xoay chậm cho Crawling, database nhồi lên xuống cho SQLi, code nhấp nháy cho XSS, CPU phóng to cho AI — những animation đặc thù này giúp người dùng nhanh chóng nhận biết bước nào đang thực thi mà không cần đọc nhãn văn bản.

> [!NOTE]
> 📷 **Hình 4.9 — Ảnh chụp trang lịch sử quét (history.html).** Cần chèn screenshot trang lịch sử với danh sách các phiên quét, badge trạng thái và nút xem kết quả.

---

## 4.7. Triển khai với Docker

Hệ thống được container hóa hoàn toàn bằng Docker để đảm bảo tính nhất quán của môi trường thực thi và đơn giản hóa quy trình triển khai. Mô hình triển khai bao gồm hai container chạy song song được quản lý bởi Docker Compose, giao tiếp với nhau thông qua mạng nội bộ Docker bridge network.

### 4.7.1. Dockerfile

Tệp `Dockerfile` định nghĩa quy trình xây dựng Docker image cho ứng dụng scanner, sử dụng kỹ thuật multi-stage caching tối ưu thời gian build. Image sử dụng `python:3.11-slim` làm base — phiên bản slim chỉ bao gồm runtime Python tối thiểu, giảm đáng kể kích thước image so với phiên bản đầy đủ. Quá trình build diễn ra qua năm bước: đặt thư mục làm việc (`WORKDIR /app`); cài đặt các thư viện hệ thống cần thiết cho lxml (`gcc`, `libxml2-dev`, `libxslt1-dev`) — lxml yêu cầu biên dịch mã C nên cần trình biên dịch gcc và các tệp header XML; sao chép và cài đặt `requirements.txt` riêng biệt trước mã nguồn để tận dụng Docker layer caching — nếu mã nguồn thay đổi nhưng danh sách thư viện không đổi, Docker sử dụng lại layer cài đặt đã cache thay vì cài lại từ đầu; sao chép toàn bộ mã nguồn; và xóa tệp SQLite cũ (`rm -f /app/instance/scanner.db`) để đảm bảo schema luôn được tạo mới phù hợp với phiên bản mã nguồn hiện tại.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Cài đặt thư viện hệ thống cho lxml
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

# Layer caching: cài thư viện Python trước
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn
COPY . .

EXPOSE 5000

# Đảm bảo schema DB luôn mới
RUN rm -f /app/instance/scanner.db /app/scanner.db

CMD ["python", "run.py"]
```

### 4.7.2. Docker Compose

Tệp `docker-compose.yml` định nghĩa hai service hoạt động song song. Service `web` (container name `ai-vuln-scanner`) build image từ Dockerfile, ánh xạ cổng 5000 ra host để truy cập giao diện web, mount thư mục mã nguồn qua volume (`- .:/app`) cho phép hot-reload trong quá trình phát triển — mọi thay đổi mã nguồn trên máy host lập tức có hiệu lực trong container mà không cần rebuild image, kết hợp với biến `FLASK_DEBUG=1` bật chế độ auto-reload của Flask. Tệp `.env` được tải tự động thông qua directive `env_file`, cung cấp các biến môi trường nhạy cảm (API keys, mật khẩu DVWA, secret key) cho ứng dụng mà không cần ghi trực tiếp trong `docker-compose.yml` hay mã nguồn.

Service `dvwa` (container name `dvwa-target`) sử dụng image sẵn có `vulnerables/web-dvwa` từ Docker Hub — image này chứa ứng dụng DVWA đã được cấu hình hoàn chỉnh trên nền Apache+PHP+MySQL, sẵn sàng sử dụng ngay sau khi khởi tạo cơ sở dữ liệu. DVWA được ánh xạ cổng 80 ra cổng 8080 trên host, cho phép truy cập trực tiếp qua trình duyệt tại `http://localhost:8080` để kiểm tra thủ công. Bên trong mạng Docker, service `web` truy cập DVWA thông qua tên container `dvwa-target` với cổng nội bộ 80, không cần cấu hình địa chỉ IP — Docker Compose tự động tạo mạng bridge và quản lý DNS resolution giữa các container.

```yaml
services:
  web:
    build: .
    container_name: ai-vuln-scanner
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - /app/__pycache__
    env_file:
      - .env
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    restart: unless-stopped

  dvwa:
    image: vulnerables/web-dvwa
    container_name: dvwa-target
    ports:
      - "8080:80"
    restart: unless-stopped
```

### 4.7.3. Quy trình khởi chạy hệ thống

Để triển khai và sử dụng hệ thống, người dùng thực hiện ba bước. Bước thứ nhất, sao chép tệp `.env.example` thành `.env` và điền các giá trị cấu hình cần thiết — tối thiểu cần có `GEMINI_API_KEY` hoặc `BLACKBOX_API_KEY` cho tính năng AI, `SECRET_KEY` cho bảo mật phiên, và các thông tin đăng nhập DVWA (mặc định `admin`/`password`). Bước thứ hai, chạy lệnh `docker-compose up --build` để build image ứng dụng (lần đầu) và khởi tạo cả hai container; sau khi hoàn tất, giao diện scanner sẵn sàng tại `http://localhost:5000` và DVWA tại `http://localhost:8080`. Bước thứ ba, truy cập DVWA tại `http://localhost:8080` lần đầu tiên để nhấn nút "Create / Reset Database" khởi tạo cơ sở dữ liệu DVWA — bước này chỉ cần thực hiện một lần duy nhất.

> [!NOTE]
> 📷 **Hình 4.10 — Mô hình triển khai Docker.** Cần chèn sơ đồ thể hiện hai container (ai-vuln-scanner trên port 5000 và dvwa-target trên port 8080) giao tiếp qua Docker bridge network, với mũi tên từ máy host truy cập cả hai container, và mũi tên nội bộ từ scanner gọi đến DVWA.

---

## 4.8. Tổng kết chương

Chương 4 đã trình bày toàn bộ quá trình triển khai hệ thống quét lỗ hổng ứng dụng web tích hợp trí tuệ nhân tạo từ bản thiết kế trong Chương 3 thành mã nguồn hoạt động. Cấu trúc dự án được tổ chức rõ ràng theo kiến trúc phân tầng với sự phân tách triệt để giữa tầng trình bày (templates), tầng điều khiển (routes), tầng dịch vụ (services) và tầng dữ liệu (models). Module Crawler triển khai thuật toán BFS duyệt web với cơ chế giới hạn cùng miền, chống trùng lặp, lọc tệp tĩnh và tự động đăng nhập DVWA. Module Detector triển khai hai bộ phát hiện lỗ hổng sử dụng phương pháp rule-based: phát hiện SQL Injection qua ba chiến lược phân tích (error-based, content length anomaly, status code change) kết hợp mô hình tính điểm có trọng số, và phát hiện XSS qua ba chiến lược (reflected payload, event handler, dangerous tag) với cơ chế loại trừ dương tính giả thông qua kiểm tra HTML encoding. Module AI Advisor triển khai kiến trúc đa nhà cung cấp (Gemini và Blackbox) với prompt engineering chuyên biệt cho bảo mật, thuật toán phân tích JSON linh hoạt, và tính năng Chat Q&A gắn ngữ cảnh lỗ hổng. Scanner Engine đóng vai trò bộ điều phối pipeline bảy bước với cơ chế xử lý lỗi toàn cục. Giao diện người dùng được xây dựng với phong cách Glassmorphism hiện đại, hiệu ứng loading animation đa lớp và tương tác AJAX không tải lại trang. Toàn bộ hệ thống được đóng gói trong hai Docker container giao tiếp qua mạng nội bộ, sẵn sàng triển khai chỉ bằng một lệnh duy nhất. Các kết quả kiểm thử thực nghiệm đánh giá hiệu quả hoạt động của hệ thống sẽ được trình bày trong **Chương 5: Kiểm thử và Đánh giá**.
