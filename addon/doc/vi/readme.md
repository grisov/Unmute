    # NVDA Bật âm thanh

* Tác giả: Oleksandr Gryshchenko
* Phiên bản: 1.5
* NVDA tương thích: 2019.3 trở lên
* Tải về [phiên bản chính thức][1]

Add-on này kiểm tra trạng thái âm thanh hệ thống của Windows khi khởi động NVDA. Nếu nhận thấy rằng âm thanh bị tắt thì add-on sẽ  bật nó lên.

Cùng thời điểm, mức độ âm lượng cũng được kiểm tra riêng biệt cho NVDA.

Add-on cũng kiểm tra trạng thái của bộ phát âm. Nếu có trục trặc với việc gọi chạy nó, add-on sẽ nỗ lực gọi bộ đọc đó lên với các thiết lập trong cài đặt của NVDA.

Có một tính năng bổ sung để kiểm tra xem thiết bị âm thanh nào đang là đầu ra âm thanh của NVDA. Nếu thiết bị này khác với thiết bị mặc định, đầu ra sẽ tự chuyển sang thiết bị mặc định.

Lưu ý: nếu âm thanh khởi động của add-on luôn phát ngay cả khi âm thanh của NVDA đã được bật. Điều đó là do add-on đã chuyển đầu ra âm thanh sang thiết bị âm thanh mặc định mỗi lần bạn khởi động NVDA.

Điều này diễn ra khi đầu ra thiết bị âm thanh trong cài đặt NVDA khác với thiết bị mặc định hoặc không phải là "Microsoft Sound Mapper".

Có thể khắc phục dễ dàng bằng một trong những cách sau:

1. Sau khi khởi động lại NVDA, chỉ việc lưu cấu hình hiện tại bằng lệnh NVDA+Ctrl+C. Thiết bị âm thanh mặc định sẽ được lưu trong cài đặt NVDA  và việc chuyển thiết bị sẽ không xảy ra mỗi khi khởi động NVDA.
2. Nếu không muốn thay đổi cấu hình của NVDA - chỉ việc tắt  tính năng chuyển thiết bị âm thanh trong bảng cài đặt bật âm thanh.

## Hộp thoại cài đặt Add-on
Để mở hộp thoại cài đặt add-on, làm theo các bước sau:

* Bấm NVDA+N để mở trình đơn NVDA.
* Vào tiếp "Cài Đặt" -> "Cấu hình...". Ở phần danh sách phân loại, tìm phân loại tên "Bật âm thanh của Windows".

Bây giờ, bạn có thể dùng phím Tab để di chuyển qua các tùy chọn của add-on.

Hiện tại, có các tùy chọn sau đây trong hộp thoại cài đặt Add-on:

1. Thanh trượt đầu tiên trong bản cài đặt add-on cho phép bạn chọn  mức âm lượng của Windows, sẽ được thiết lập khi khởi động NVDA mà âm thanh đã bị tắt trước đó hoặc âm lượng quá nhỏ.

2. Mức âm lượng tối thiểu của Windows là ngưỡng để áp dụng việc tăng âm lượng. Thanh trượt này cho phép bạn chọn ngưỡng âm thanh cho add-on.

Nếu mức âm lượng nhỏ hơn giá trị thiết lập ở đây, nó sẽ được tăng lên ở lần khởi động NVDA tiếp theo.

Còn nếu mức âm lượng lớn hơn giá trị được thiết lập ở đây, nó sẽ không bị thay đổi khi bạn khởi động lại NVDA.

Và dĩ nhiên, nếu âm thanh đã bị tắt trước đó, khi khởi động lại, add-on sẽ bật nó lên.

3. Các hộp kiểm sau đây cho phép bật khởi động lại trình điều khiển của bộ đọc.

Việc này chỉ thực hiện khi nhận thấy NVDA khởi động mà không khởi động trình điều khiển bộ đọc.

4. Ở trường này, bạn có thể thiết lập số lần  nỗ lực khởi động lại trình điều khiển bộ đọc. Việc này được thực hiện theo chu kì với mỗi lần cách nhau 1 giây.

5. Tùy chọn "Chuyển sang thiết bị âm thanh mặc định" cho phép kiểm tra khi khởi động xem NVDA đang dùng thiết bị nào cho đầu ra âm thanh của mình. Nếu thiết bị này khác với thiết bị âm thanh mặc định, đầu ra sẽ tự chuyển sang thiết bị âm thanh mặc định.

6. Hộp kiểm tiếp theo bật hoặc tắt việc phát âm thanh khởi động khi mọi thứ được xử lý xong.

## Các thành phần của bên thứ ba
Add-on sử dụng các thành phần sau của bên thứ ba:

* Để tương tác với **Windows Core Audio API** - [PyCaw module](https://github.com/AndreMiras/pycaw/) phân phối theo giấy phép MIT.
* Để lấy thông tin về các ứng dụng đang chạy cũng như sử dụng PyCaw - [psutil module](https://github.com/giampaolo/psutil) phân phối theo giấy phép BSD-3.

## Các thay đổi

### Phiên bản 1.5.5
* Add-on đã được kiểm nghiệm tính tương thích với NVDA 2021.1;
* Cập nhật module của bên thứ ba ** psutil **;
* Add-on được tích hợp hỗ trợ Python phiên bản 3.7 và 3.8;
* MyPy type annotations đã được thêm vào mã nguồn của add-on;
 * Đã thêm tính năng   "Chuyển sang thiết bị đầu ra âm thanh mặc định".
 * Tham số của add-on được lưu vào hồ sơ cấu hình cơ sở;
 * Đã thêm các bản dịch tiếng Tây Ban Nha và Galician (cảm ơn Ivan Novegil Cancelas và Jose Manuel).
 
 ### Phiên bản 1.4
* Đã thêm phương thức tăng âm lượng khởi động độc lập cho việc vận hành NVDA;
* Thay đổi âm thanh thông báo cho các hoạt động thành công (cảm ơn Manolo);
* Tất cả các chức năng điều khiển âm lượng thủ công đã được chuyển qua add-on NVDA Volume Adjustment.

### Phiên bản 1.3
* Thêm khả năng điều khiển âm lượng của thiết bị âm thanh tổng và điều khiển độc lập cho mỗi chương trình đang chạy;
* Cập nhật bản phiên dịch tiếng Việt (cảm ơn Đặng Mạnh Cường);
* Đã thêm bản phiên dịch tiếng Thổ Nhĩ Kỳ (cảm ơn Cagri Dogan);
* Đã thêm bản phiên dịch tiếng Ý (cảm ơn Christianlm); 
* Đã thêm bản phiên dịch tiếng Trung Quốc giản thể (Cảm ơn Cary Rowen); 
* Cập nhật bản phiên dịch tiếng Ukraina;

* Cập nhật tập tin Readme.

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

## Tùy biến mã nguồn của add-on
Bạn có thể tạo bản sao (clone) cho add-on này để thực hiện các tùy biến cho nó.

### Các thư viện phụ thuộc của bên thứ ba
Chúng có thể được cài đặt với pip:
- markdown
- scons
- python-gettext

### Để đóng gói và phân phối add-on:
1. Mở một ứng dụng dòng lệnh, điều hướng đến thư mục gốc của kho add-on này
2. Gõ lệnh **scons**. Gói add-on sẽ được tạo ở thư mục hiện tại nếu không có lỗi xảy ra.

[1]: https://github.com/grisov/Unmute/releases/download/latest/unmute-1.5.2.nvda-addon
[2]: https://github.com/grisov/Unmute/releases/download/latest/unmute-1.5.3-dev.nvda-addon
