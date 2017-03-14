#Các kịch bản thao tác trong hệ thống

###1. Kịch bản Đăng ký tài khoản.

- Đầu vào: Thông tin xác thực của tài khoản User.
- User lựa chọn hình thức đăng ký (SignUp with Email, Username & Password hoặc
  Social Authentication).
- Email-User-Password: Người dùng nhập thông tin, sau đó sẽ có email xác thực
  đến địa chỉ email đã đăng ký.
- Social Authentication.
- Hệ thống tiếp nhận thông tin xác thực của User, lưu vào database.
- Đầu ra: Kết quả tạo tài khoản. Thành công hay thất bại.

##2. Kịch bản Đăng nhập tài khoản.

- Đầu vào: Thông tin xác thực của tài khoản User.
- User nhập các thông tin đăng nhập/Lựa chọn login with Social Account.
- Hệ thống thực hiện truy vấn đến database để kiểm tra xác thực.
- Đầu ra: Đăng nhập thành công và redirect đến trang Dashboard. Thất bại sẽ
  hiển thị thông báo.

##3. Kịch bản Khởi tạo CloudRing.

- Đầu vào: file cloud_config hoặc cho phép người dùng nhập từng cloud một
  (theo form xác định trước).
- Hệ thống tiếp nhận cloud config. Khởi tạo đối tượng CloudServer - đóng vai
  trò 1 node trong CloudRing (id(được hash từ ip address..), cloudconfig,...)
- Lưu thông tin CloudServer vào Database.
- Khởi tạo CloudRing với các Node là CloudServer đã có.
- Đầu ra: Hiển thị danh sách cloud đã có.

##4. Kịch bản Tạo và upload file (folder-chỉ là giả lập)

- Đầu vào: Đường dẫn đến file cần upload.(có thể dùng thao tác drag and drop).
  Nhập filename.
- User cung cấp, chọn file cần upload và filename.
- Hệ thống tiếp nhận file, tách thành 2 phần filename và content. filename sẽ
  được hashing tạo nên id cho file. Sau đó tạo các replica bằng cách thêm
  hậu tố, ví dụ filename "this\_is\_object.txt" --> "this\_is\_object_01.txt" ,...
  Số lượng replica sẽ được config trước đó.
- Hệ thống tiếp tục hashing replica name, tạo các id của replica.
- Lưu các thông tin về id, danh sách replicas (đi kèm trạng thái hiện tại
  replica: updated or not_update) và lịch sử giao dịch và database.
- Dựa vào id của các replica, tìm các CloudServer trong CloudRing sẽ lưu
  content (Cần có cơ chế tránh lưu các replica trong cùng một CloudServer).
  Tiến hành đẩy request PUT content về phía CloudServer.
- Sau khi PUT thành công tại 1 replica, cập nhật trạng thái replica = updated.
- Đầu ra: Thông báo tạo thành công hay không.. Hiển thị file ra giao diện.

##5. Kịch bản Xóa file.

- Đầu vào: File được User chọn xóa.
- Từ filename, id có thể lấy được danh sách các replica của DataObject (tức file).
- Sử dụng Chord protocol, đẩy replica id vào trong CloudRing để tiến hành lookup.
  Biết được CloudServer đang chứa replica, tiến hành gửi Request DELETE xuống
  CloudServer đó.
- Để lại 1 replica mang tính chất backup trong trường hợp User muốn thay đổi, lấy
  lại file đã xóa.
- Đầu ra: Thông báo xóa thành công hay không. Thông báo sau 30 ngày sẽ thực sự xóa toàn bộ
  file (Tất cả các object).

##6. Kịch bản Download file.

- Đầu vào: User chọn file muốn download.
- Từ filename, id có thể lấy được danh sách các replica của DataObject (tức file).
- Lựa chọn replica trong dánh sách các replica.
- Sử dụng Chord protocol, đẩy replica id vào trong CloudRing để tiến hành lookup.
  Biết được CloudServer đang chứa replica, tiến hành gửi Request GET xuống
  CloudServer đó.
- Đầu ra: Download file. Thông báo download thành công hay không.

##7. Kịch bản Update file.

- Đầu vào: User chọn file muốn update và upload version mới cho file.
- Đưa bản update (filename và content) vào cache queue.
- Nếu đến lượt bản update, dựa vào filename, id tìm ra danh sách replica.
- Lựa chọn replica trong danh sách đó.
- Tiến hành PUT content đến CloudServer chứa replica (Dựa vào CloudRing và chord để
  tìm ra được vị trí của replica). Content mới sẽ thay thế content cũ, replica được
  cập nhật. Chuyển trạng thái của replica về updated = True, các replica khác
  updated = False. Khi có request đến SCS, yêu cầu file này, request sẽ được chuyển
  hướng ưu tiên đến replica với trạng thái updated = True.
- Định kỳ, sau một khoảng thời gian t, `daemon process` tiếp tục đẩy bản update trong
  cache queue đến các replica còn lại (Cần có cơ chế tránh lưu các replica trong
  cùng một CloudServer). Cập nhật trạng thái sau khi đẩy xong, updated = True.
  (Những thông tin về trạng thái sẽ được lưu dưới DB). Khi tất cả các replica có
  trạng thái updated = True, loại bỏ bản update khỏi cache queue.
- Đầu ra: Thông báo update thành công hay không(ngay sau khi cập nhật replica đầu tiên)

##8. Kịch bản Thêm mới CloudServer.

- Đầu vào: User chọn Thêm CloudServer vào CloudRing. Nhập vào cấu hình cloud
  (Cloud config, ip address...)
- Join CloudServer vào CloudRing (theo cơ chế join node trong Chord).
- Lưu thông tin CloudServer vào database.
- Đầu ra: Thông báo thêm thành công hay không.

##9. Kịch bản Loại bỏ CloudServer.

- Đầu vào: User lựa chọn CloudServer cần loại bỏ khỏi CloudRing.
- Thực hiện Leave CloudRing (Theo cơ chế leave trong Chord).
- Xóa thông tin về CloudServer đó khỏi DB.
- Đầu ra: Thông báo xóa thành công hay không.

##10. Kịch bản Thay đổi UserProfile. (optional)

- Đầu vào: User lựa chọn thay đổi User profile.
- Thay đổi các thông tin của User Profile (ảnh đại diện, username, ...)
- Đầu ra: Thông báo thay đổi thành công hay không. Hiển thị thay đổi.

##11. Quản lý các user (admin-optional)

##12. Kiểm tra status của các CloudServer.

- Giải pháp: `daemon process` định kỳ bản tin về phía CloudServer.
- Ping đến CloudServer?
- Bắn bản tin đến CloudServer theo ip và port. (Với AmazonS3?)
- Check health qua API?
