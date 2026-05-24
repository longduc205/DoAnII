# PHẦN MỞ ĐẦU

### Lý do chọn đề tài

Trong bối cảnh kỷ nguyên số và sự phát triển mạnh mẽ của Internet, các ứng dụng web đã trở thành nền tảng không thể thiếu đối với mọi lĩnh vực từ thương mại điện tử, tài chính, giáo dục đến chính phủ điện tử. Sự gia tăng cả về số lượng lẫn độ phức tạp của các ứng dụng này kéo theo hàng loạt rủi ro về an toàn thông tin. Các cuộc tấn công mạng nhằm vào lỗ hổng ứng dụng web không ngừng gia tăng về quy mô và mức độ tinh vi, gây ra những hậu quả nghiêm trọng như rò rỉ dữ liệu nhạy cảm, gián đoạn dịch vụ và tổn thất về mặt tài chính cũng như uy tín của tổ chức. Trong bối cảnh đó, việc phát hiện và khắc phục kịp thời các lỗ hổng bảo mật trước khi chúng bị lợi dụng trở thành một yêu cầu cấp thiết. Mặc dù trên thị trường đã có nhiều công cụ quét lỗ hổng tự động (scanner), tuy nhiên đa số các công cụ này chỉ dừng lại ở việc cảnh báo kỹ thuật, thiếu đi khả năng giải thích nguyên nhân gốc rễ và hướng dẫn khắc phục chi tiết một cách dễ hiểu. Việc tích hợp Trí tuệ Nhân tạo (AI) vào hệ thống quét lỗ hổng mang lại tiềm năng to lớn để giải quyết hạn chế này, biến các cảnh báo khô khan thành những tư vấn chuyên sâu, giúp giảm tải công sức cho chuyên gia bảo mật và hỗ trợ các nhà phát triển phần mềm khắc phục lỗ hổng một cách hiệu quả hơn. Đó là lý do cốt lõi để tác giả lựa chọn đề tài "Xây dựng hệ thống quét lỗ hổng web tích hợp trí tuệ nhân tạo" cho Đồ án II.

### Mục tiêu đề tài

Mục tiêu chính của đề tài là nghiên cứu, thiết kế và xây dựng một hệ thống phần mềm (prototype) có khả năng tự động rà quét và phát hiện các lỗ hổng bảo mật phổ biến trên ứng dụng web, cụ thể là SQL Injection (SQLi) và Cross-Site Scripting (XSS). Không chỉ dừng lại ở chức năng phát hiện, hệ thống còn đặt mục tiêu tích hợp năng lực của Trí tuệ Nhân tạo sinh (Generative AI) thông qua API để tự động phân tích các lỗ hổng đã được tìm thấy, từ đó sinh ra các báo cáo tư vấn khắc phục chi tiết, bao gồm giải thích cơ chế khai thác, đánh giá mức độ nghiêm trọng và cung cấp các đoạn mã nguồn minh họa cho việc vá lỗi. Đề tài hướng tới việc chứng minh tính khả thi của việc kết hợp AI vào quy trình đánh giá bảo mật ứng dụng.

### Phạm vi đề tài

Do giới hạn về thời gian thực hiện đồ án cũng như mục tiêu hướng tới tính học thuật và nghiên cứu nguyên lý, phạm vi của hệ thống được thu hẹp tập trung vào việc nhận diện hai loại lỗ hổng phổ biến và nguy hiểm nhất theo phân loại của OWASP là SQL Injection và Reflected Cross-Site Scripting (XSS). Hệ thống không bao quát toàn bộ các tiêu chuẩn của một phần mềm thương mại. Về môi trường thử nghiệm, toàn bộ quá trình kiểm thử và đánh giá độ chính xác của hệ thống được thực hiện trên Damn Vulnerable Web Application (DVWA) — một ứng dụng web mã nguồn mở được thiết kế đặc biệt với các lỗ hổng có chủ đích phục vụ cho việc học tập và nghiên cứu. Đề tài không thực hiện quét đối với các hệ thống đang hoạt động thực tế trên Internet khi chưa có sự cho phép để đảm bảo tuân thủ các quy định về an ninh mạng và đạo đức nghề nghiệp.

### Phương pháp nghiên cứu

Đề tài sử dụng kết hợp hai phương pháp nghiên cứu chính: phương pháp nghiên cứu lý thuyết và phương pháp thực nghiệm. Đối với phương pháp nghiên cứu lý thuyết, tác giả tiến hành thu thập, tổng hợp và phân tích các tài liệu học thuật, báo cáo bảo mật từ OWASP, cũng như kiến trúc của các công cụ bảo mật hiện có. Quá trình này giúp xây dựng nền tảng kiến thức vững chắc về các loại lỗ hổng web và nguyên lý hoạt động của các hệ thống scanner. Đối với phương pháp thực nghiệm, tác giả tiến hành phân tích thiết kế hệ thống, lựa chọn công nghệ (Python, Flask, Docker, và các API AI) để lập trình và xây dựng một phần mềm nguyên mẫu (prototype). Cuối cùng, phương pháp thực nghiệm được áp dụng để kiểm thử phần mềm trên môi trường DVWA, tiến hành đo lường các chỉ số hiệu năng như tỉ lệ phát hiện (Detection Rate) và phân tích độ chính xác trong các tư vấn của AI nhằm rút ra các kết luận khách quan.

### Cấu trúc báo cáo

Báo cáo đồ án được cấu trúc thành 5 chương chính, bao gồm:

*   **Chương 1: Tổng quan.** Giới thiệu bài toán an toàn thông tin web, điểm qua các nghiên cứu và công cụ hiện có, từ đó đề xuất hệ thống với kiến trúc quét kết hợp AI và nêu bật lợi ích kỳ vọng.
*   **Chương 2: Cơ sở lý thuyết.** Cung cấp nền tảng lý thuyết về lỗ hổng ứng dụng web (cụ thể là SQL Injection và XSS), nguyên lý hoạt động của các hệ thống tự động phát hiện lỗ hổng và cơ chế ứng dụng Large Language Models (LLMs) trong lĩnh vực an toàn thông tin.
*   **Chương 3: Phân tích thiết kế hệ thống.** Trình bày chi tiết kiến trúc tổng thể, mô hình dữ liệu, sơ đồ luồng hoạt động của các module cốt lõi bao gồm Crawler, Vulnerability Detector và hệ thống AI Advisor.
*   **Chương 4: Triển khai hệ thống.** Trình bày quá trình xây dựng hệ thống trong thực tế, bao gồm lựa chọn công nghệ, cấu trúc mã nguồn, và mô tả chi tiết việc lập trình các module chức năng cũng như tích hợp API trí tuệ nhân tạo.
*   **Chương 5: Kiểm thử và đánh giá.** Mô tả quá trình triển khai môi trường kiểm thử với DVWA, thực hiện các kịch bản đánh giá chức năng, đo lường hiệu năng tổng thể, so sánh với các công cụ tương đương và đưa ra phân tích thẳng thắn về hạn chế của hệ thống.

---

# CHƯƠNG 1: TỔNG QUAN

## 1.1. Giới thiệu bài toán

### 1.1.1. An toàn thông tin web trong bối cảnh hiện nay

Trong bối cảnh chuyển đổi số đang diễn ra mạnh mẽ trên toàn cầu, các ứng dụng web đã vượt qua giới hạn của những trang hiển thị thông tin tĩnh để trở thành các hệ thống dịch vụ phức tạp, xử lý khối lượng lớn dữ liệu cá nhân, tài chính và y tế. Điều này đã biến ứng dụng web trở thành mục tiêu hấp dẫn hàng đầu của tội phạm mạng. Các chiến dịch tấn công hiện đại không chỉ tập trung vào việc thay đổi giao diện (defacement) mang tính biểu diễn như trước đây, mà chuyển hướng sang trục lợi tài chính, đánh cắp cơ sở dữ liệu khách hàng, đánh cắp bí mật kinh doanh, hoặc sử dụng máy chủ bị thỏa hiệp như một phần của mạng botnet tấn công từ chối dịch vụ (DDoS) và đào tiền ảo. Tính phức tạp trong kiến trúc phần mềm, sự phụ thuộc sâu rộng vào các thư viện mã nguồn mở của bên thứ ba, cùng với áp lực rút ngắn vòng đời phát triển phần mềm (Agile/DevOps) đã khiến cho việc đảm bảo an ninh từ giai đoạn viết mã trở nên khó khăn hơn, dẫn đến sự tồn tại dai dẳng của các lỗ hổng bảo mật trên ứng dụng thực tế.

### 1.1.2. Thống kê tấn công web và OWASP Top 10

Tổ chức phi lợi nhuận OWASP (Open Worldwide Application Security Project) định kỳ phát hành báo cáo OWASP Top 10, một tài liệu chuẩn mực nhận diện các rủi ro bảo mật nghiêm trọng nhất đối với ứng dụng web dựa trên dữ liệu thống kê từ hàng trăm ngàn ứng dụng trên toàn cầu. Các lỗ hổng thuộc nhóm Injection (tiêm nhiễm), đặc biệt là SQL Injection, liên tục góp mặt trong các phiên bản OWASP Top 10 xuyên suốt hơn một thập kỷ, do khả năng cho phép kẻ tấn công trích xuất trực tiếp toàn bộ dữ liệu từ hệ quản trị cơ sở dữ liệu. Tương tự, Cross-Site Scripting (XSS) — lỗ hổng cho phép thực thi mã độc trên trình duyệt của nạn nhân — cũng luôn là một trong những vector tấn công phổ biến nhất nhằm đánh cắp phiên làm việc (session hijacking) và thực hiện các hành vi lừa đảo (phishing). Sự tồn tại dai dẳng của các loại lỗ hổng kinh điển này cho thấy sự thiếu hụt trong các biện pháp kiểm soát an ninh tại khâu phát triển, bất chấp việc lý thuyết phòng thủ đối với chúng đã được chuẩn hóa từ lâu.

### 1.1.3. Nhu cầu tự động hóa kiểm thử bảo mật

Kiểm thử bảo mật thủ công (Manual Penetration Testing) mang lại độ chính xác cao nhờ sự kết hợp giữa kiến thức chuyên sâu và khả năng phân tích ngữ cảnh của chuyên gia con người. Tuy nhiên, phương pháp này đòi hỏi chi phí lớn, mất nhiều thời gian và khó có thể thực hiện thường xuyên mỗi khi mã nguồn có sự thay đổi. Khi quy trình CI/CD (Continuous Integration / Continuous Deployment) trở thành tiêu chuẩn trong kỹ nghệ phần mềm hiện đại, yêu cầu tự động hóa việc rà quét lỗ hổng trở nên bắt buộc. Tuy nhiên, một hệ thống phát hiện tự động nếu chỉ trả về danh sách cảnh báo khô khan sẽ trở thành gánh nặng cho đội ngũ phát triển, do họ phải tự tìm hiểu ý nghĩa cảnh báo, loại bỏ cảnh báo giả (false positives) và tìm kiếm giải pháp vá lỗi phù hợp. Vì vậy, bài toán đặt ra không chỉ là nâng cao tính tự động hóa trong khâu phát hiện, mà còn là tự động hóa khâu phân tích và cung cấp hướng dẫn khắc phục nhằm thu hẹp khoảng cách giữa phát hiện và giải quyết lỗ hổng.

## 1.2. Các nghiên cứu và công cụ liên quan

### 1.2.1. Các công cụ scanner phổ biến

Trên thị trường hiện nay có sự hiện diện của nhiều công cụ quét lỗ hổng web từ cả cộng đồng mã nguồn mở lẫn các giải pháp thương mại, mỗi công cụ đều có thế mạnh riêng. OWASP ZAP (Zed Attack Proxy) là một dự án mã nguồn mở tiêu biểu, hoạt động như một proxy trung gian với hàng ngàn luật phát hiện, được cộng đồng đánh giá cao về khả năng mở rộng. Burp Suite (phiên bản Professional) của PortSwigger là công cụ thương mại được sử dụng rộng rãi nhất bởi các chuyên gia penetration testing, nổi bật với khả năng chặn bắt linh hoạt, công cụ Intruder để brute-force, và một module active scanner hoạt động rất hiệu quả trong việc tìm kiếm Injection và XSS. Ngoài ra, các giải pháp Enterprise như Acunetix và Nessus lại tập trung vào việc thu thập diện rộng, cung cấp giao diện quản lý đa nhiệm và sinh báo cáo tuân thủ tự động (compliance reporting) cho các tổ chức lớn.

### 1.2.2. Các nghiên cứu về ứng dụng AI trong an toàn thông tin

Trong vài năm trở lại đây, sự bùng nổ của Trí tuệ Nhân tạo, đặc biệt là Học máy (Machine Learning) và các Mô hình Ngôn ngữ Lớn (LLMs), đã mở ra nhiều hướng tiếp cận mới trong lĩnh vực an toàn thông tin. Nhiều nghiên cứu học thuật đã đề xuất sử dụng mạng nơ-ron học sâu (Deep Learning) để phân loại payload XSS/SQLi dựa trên phân tích đặc trưng văn bản, nhằm thay thế các luật phát hiện truyền thống tĩnh cứng. Đối với khía cạnh phòng thủ, các mô hình học máy được triển khai trong Web Application Firewall (WAF) để nhận diện các yêu cầu HTTP bất thường. Gần đây nhất, sự xuất hiện của các mô hình LLM như GPT, Gemini và Claude đã thu hút sự chú ý của giới nghiên cứu trong việc tự động giải thích mã nguồn (code explanation), sinh mã (code generation), và tư vấn khắc phục lỗ hổng. Các nghiên cứu chỉ ra rằng LLMs có khả năng suy luận mạnh mẽ, biến các thông tin kỹ thuật rời rạc thành các báo cáo dễ hiểu.

### 1.2.3. Hạn chế của các công cụ hiện tại

Mặc dù có nhiều tính năng ưu việt, các công cụ quét lỗ hổng truyền thống vẫn tồn tại một số hạn chế cố hữu. Hạn chế lớn nhất là việc cung cấp quá ít ngữ cảnh và hướng dẫn cho người dùng cuối — đặc biệt là với các lập trình viên không chuyên về bảo mật. Các báo cáo trả về thường chỉ là một danh sách URL kèm theo chuỗi payload tĩnh và nhãn mức độ nghiêm trọng. Chúng không thể nhận thức được stack công nghệ cụ thể của ứng dụng mục tiêu để đưa ra lời khuyên vá lỗi bằng ngôn ngữ tương ứng (ví dụ: tư vấn sử dụng Prepared Statements bằng PHP PDO thay vì mysqli). Hơn nữa, các công cụ này thiếu tính tương tác; người dùng không thể đặt câu hỏi trực tiếp để hiểu rõ hơn về lý do một payload lại thành công hoặc cách kiểm tra tính hiệu quả của bản vá. Đây chính là khoảng trống mà trí tuệ nhân tạo sinh (Generative AI) có khả năng lấp đầy.

## 1.3. Đề xuất hệ thống

### 1.3.1. Mô tả ngắn gọn giải pháp

Để giải quyết các vấn đề đã nêu, đề tài đề xuất xây dựng một hệ thống quét lỗ hổng web tích hợp với AI (Web Scanner + AI Advisor). Giải pháp bao gồm hai thành phần cốt lõi hoạt động liên kết. Thành phần thứ nhất là một động cơ quét (Scanner Engine) tự động thực hiện quá trình thu thập liên kết (Crawling), phân tích biểu mẫu và tiêm các bộ payload đặc thù để kích hoạt lỗ hổng SQLi và XSS, kết hợp sử dụng nhiều chiến lược heuristic để đánh giá điểm tin cậy của phản hồi nhận được. Thành phần thứ hai là một AI Advisor, hoạt động dựa trên việc tổng hợp kết quả phân tích từ động cơ quét để đóng gói thành các đoạn prompt có cấu trúc và gửi đến API của các mô hình ngôn ngữ lớn (Google Gemini, Blackbox AI). Thành phần AI sau đó đảm nhiệm việc sinh ra các diễn giải kỹ thuật và hướng dẫn khắc phục dựa trên ngữ cảnh phát hiện.

### 1.3.2. Lợi ích kỳ vọng

Hệ thống được kỳ vọng sẽ mang lại một cách tiếp cận hoàn thiện hơn đối với quá trình đánh giá bảo mật web cơ bản. Đối với khâu rà soát, hệ thống đáp ứng nhu cầu tự động hóa trong việc phát hiện nhanh chóng hai dạng lỗ hổng phổ biến là SQL Injection và XSS với giao diện web thân thiện, dễ vận hành ngay cả với người không chuyên. Đối với khâu khắc phục, thay vì để người dùng tự tìm kiếm giải pháp trên Internet, hệ thống cung cấp các tư vấn có chiều sâu trực tiếp ngay trong giao diện kết quả. Các tư vấn này giải thích tường minh cơ chế tấn công, cung cấp mã nguồn minh họa bằng ngôn ngữ lập trình phù hợp và cho phép trò chuyện hỏi đáp (Chat Q&A) để làm rõ vấn đề. Từ đó, hệ thống không chỉ là một công cụ kiểm tra bảo mật mà còn đóng vai trò như một nền tảng hỗ trợ học tập, giúp nâng cao nhận thức và năng lực viết mã an toàn cho các nhà phát triển phần mềm.
