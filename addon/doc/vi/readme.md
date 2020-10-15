# NVDA Bật âm thanh

* Tác giả: Oleksandr Gryshchenko
* Phiên bản: 1.2
* Tải về [phiên bản chính thức][1]
* Tải về [phiên bản thử nghiệm][2]

Add-on này kiểm tra trạng thái âm thanh hệ thống của Windows khi khởi động NVDA. Nếu nhận thấy rằng âm thanh bị tắt thì add-on sẽ  bật nó lên.
Add-on cũng kiểm tra trạng thái của bộ phát âm. Nếu có trục trặc với việc gọi chạy nó, add-on sẽ nỗ lực gọi bộ đọc đó lênvới các thiết lập trong cài đặt của NVDA.

## Hộp thoại cài đặt Add-on
Hiện tại, có các tùy chọn sau đây trong hộp thoại cài đặt Add-on:
1. Tùy chọn cho phép bật âm thanh hệ thống với mức âm lượng lớn nhất khi khởi động NVDA.
2. Nếu hộp kiểm nói trên không được chọn, bạn có thể dùng thanh trượt để điều chỉnh mức độ âm lượng của âm thanh hệ thống sẽ được thiết lập khi khởi động NVDA.
3. Thanh trượt điều chỉnh mức độ âm lượng tối thiểu khi không áp dụng hai tùy chọn ở trên.

Lưu ý: tùy chọn một và hai áp dụng trong các trường hợp sau:
* Hệ thống âm thanh của Windows đã bị tắt trước khi gọi chạy NVDA;
* Khi mức độ âm thanh hệ thống thấp hơn  giá trị được đặt bởi thanh trượt thứ ba 3.

4. Các hộp kiểm sau đây cho phép bật khởi động lại trình điều khiển của bộ đọc.
Việc này chỉ thực hiện khi nhận thấy rằng NVDA khởi động mà không khởi động trình điều khiển bộ đọc.

5. Ở trương này, bạn có thể thiết lập số lần  nỗ lực khởi động lại trình điều khiển bộ đọc.

6. Hộp kiểm tiếp theo bật / tắt việc phát âm thanh khởi động  khi hoàn thành việc khởi động lại trình điều khiển bộ đọc.
## Các thay đổi

### Phiên bản 1.2
* Chuyển sang dùng **pycaw** module thay cho **Windows Sound Manager**;
* Thêm âm thanh khởi động khi audio đã được add-on bật lên.

### Phiên bản 1.1
* Thêm hộp thoại cài đặt add-on;
* Cập nhật bản dịch tiếng Ukraina.

### Phiên bản 1.0.1
* Thực hiện lặp đi lặp lại việc nỗ lực bật trình điều khiển bộ đọc trong trường hợp bị lỗi khi được gọi;
* Dịch ra tiếng Việt bởi Đặng Mạnh Cường;
* Thêm bản dịch tiếng Ugraina.

### Phiên bản 1.0. Thực hiện tính năng
Add-on sử dụng một module của bên thứ ba [Windows Sound Manager][2].

## Tùy biến NVDA Bật âm thanh
Bạn có thể tạo bản sao (clone) cho add-on này để thực hiện các tùy biến cho nó.

### Các thư viện phụ thuộc của bên thứ ba
Chúng có thể được cài đặt với pip:
- markdown
- scons
- python-gettext

### Để đóng gói và phân phối add-on:
1. Mở một ứng dụng dòng lệnh, điều hướng đến thư mục gốc của kho add-on này
2. Gõ lệnh **scons**. Gói add-on sẽ được tạo ở thư mục hiện tại nếu không có lỗi xảy ra.

[1]: https://github.com/grisov/Unmute/releases/download/v1.2/unmute-1.2.nvda-addon
[2]: https://github.com/grisov/Unmute/releases/download/v1.2/unmute-1.2.nvda-addon
