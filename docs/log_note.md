# Log Note: Ghi chú những vấn đề gặp phải trong quá trình xây dựng hệ thống

## 18/3/2017

Vấn đề 1: **Giới hạn phạm vi của hệ thống**

Hệ thống được xác định giới hạn phạm vi làm việc như sau:

- Số người dùng hệ thống ở mức độ vừa phải
- Kích thước tệp tin trong hệ thống không quá lớn
- Dung lượng các Cloud Server mà người dùng có là đồng đều với nhau.

Vấn đề 2: **Thêm mới CloudNode vào CloudRing - Các bước xử lý**

1. Tạo CloudID cho Cloud Server mới thêm.
1. Thiết lập CloudRing, thêm Cloud mới tạo vào Cloud Ring theo Chord Protocol. Cập nhật bảng định tuyến cho các Node trong Cloud Ring và cập nhật thông tin định tuyến cho các node nằm ở phía trước và phía sau node mới được thêm vào.
1. Quét danh sách các Replica hiện có trên Successor Node, kiểm tra xem các Replica nào cần phải di chuyển theo Chord Protocol.
1. Chuyển status của Cloud Node mới thêm và Successor Node của nó sang trạng thái **IS\_TRANSFERING\_DATA**. Tạo ra một **Move Data Daemon Process** di chuyển các Replica của các Data Object sai vị trí sang Cloud Node mới.
1. Sau khi di chuyển dữ liệu xong, chuyển lại trạng thái cho Cloud Node mới và Successor Node sang **READY**

Vấn đề xảy ra: Trong Các Replica cần di chuyển có một số Replica không ở trạng thái READY mà đang ở trạng thái UPDATING, vvv....?