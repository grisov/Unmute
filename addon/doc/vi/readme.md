# NVDA Bật âm thanh

* Tác giả: Oleksandr Gryshchenko
* Phiên bản: 1.0
* Tải về [phiên bản chính thức][1]

Add-on này kiểm tra trạng thái âm thanh hệ thống của Windows khi khởi động NVDA. Nếu nhận thấy rằng âm thanh bị tắt thì add-on sẽ  bật nó lên.
Add-on cũng kiểm tra trạng thái của bộ phát âm. Nếu có trục trặc với việc gọi chạy nó, add-on sẽ nỗ lực gọi bộ đọc đó lênvới các thiết lập trong cài đặt của NVDA.

## Các thay đổi

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

[1]: https://github.com/grisov/Unmute/releases/download/v1.0/unmute-1.0.nvda-addon
[2]: https://github.com/Paradoxis/Windows-Sound-Manager
