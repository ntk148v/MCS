# Phân tích yêu cầu và thiết kế chức năng hệ thống Multi Cloud Storage (MCS)

## 1. Giới thiệu

Hệ thống Multi Cloud Storage (MCS) là một hệ thống cho phép kết hợp tất cả các cơ sở lưu trữ mà người dùng đang có thành một kho lưu trữ thống nhất. Kho lưu trữ thống nhất sau khi được xây dựng sẽ cung cấp cho người dùng năng lực lưu trữ của tất cả các đám mây mà người dùng đang có, đồng thời có những tính năng nổi bật sau:

- High-availability
- Scalable
- Fault-tolerance
- Load-balancing
- Redundancy storage

Bên cạnh những tính năng trên, hệ thống MCS đảm bảo các tương tác với dữ liệu của người dùng như lưu trữ, truy cập thay đổi dữ liệu... được thực hiện một cách tối ưu - optimize nhất.

## 2. Mục tiêu của hệ thống

Hệ thống MCS được xây dựng để thực hiện hai mục tiêu chính sau:

- Quản lý Data Object: Cho phép người dùng sử dụng hệ thống để lưu trữ và quản lý các Data Object bằng các thao tác như lấy về Object Data, tạo mới, di chuyển, cập nhật, xóa bỏ Data Object. Trong trường hợp Upload, cho người dùng lựa chọn số lượng bản sao của một Data Object, cho phép người dùng lựa chọn một trong 2 chế độ: hoặc người dùng tự xác định Cloud nào sẽ lưu trữ bản sao của Data Object, hoặc hệ thống sẽ tự động lựa chọn các Cloud phù hợp.

- Quản lý Cloud Server: Cho phép người dùng cấu hình danh sách các Cloud Server mà người dùng có trên hệ thống, cho phép thêm mới và gỡ bỏ các Cloud Server khỏi hệ thống. Khi người dùng thực hiện thao tác gỡ bỏ Cloud Server khỏi hệ thống, hệ thống cho phép người dùng lựa chọn xem có giữ lại các Data Object đang lưu trữ trên Cloud Server đó ( di chuyển các Data Object nằm trên Cloud Server bị gỡ bỏ sang các Cloud Server còn lại của hệ thống) hay không. Bên cạnh đó, hệ thống cho phép người dùng kiểm tra trạng thái của các Cloud Server.


## 3. Thiết kế biểu đồ lớp của hệ thống

Dựa vào những gì đã phân tích ở tài liệu thiết kế hệ thống, biểu đồ lớp của hệ thống được xây dựng như sau:

![class_diagram](./images/class_diagram.png)

## 4. Thiết kế cơ chế xử lý các ca sử dụng của người dùng

## 1. Kịch bản Đăng ký tài khoản.

### Input

Thông tin xác thực của tài khoản User.

### Các bước xử lý

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
  replica: updated = True or False) và lịch sử giao dịch và database.
- Dựa vào id của các replica, tìm các CloudServer trong CloudRing sẽ lưu
  content (Cần có cơ chế tránh lưu các replica trong cùng một CloudServer).
  Tiến hành đẩy request PUT content về phía CloudServer.
- Sau khi PUT thành công tại 1 replica, cập nhật trạng thái replica.updated = True.
- Khi tất cả các replica được PUT thành công, cập nhật trạng thái của DataObject.

```python
  dataobject.synced = all(replica.updated = True for replica in dataobject.replicas)
```

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
  CloudServer đó. Ưu tiên chọn những replica.updated = True.
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
  trạng thái updated = True, loại bỏ bản update khỏi cache queue và chuyển trạng thái
  của DataObject: synced = True.

```python
  dataobject.synced = all(replica.updated = True for replica in dataobject.replicas)
```

- Đầu ra: Thông báo update thành công hay không(ngay sau khi cập nhật replica đầu tiên)

##8. Kịch bản Thêm mới CloudServer.

- Đầu vào: User chọn Thêm CloudServer vào CloudRing. Nhập vào cấu hình cloud
  (Cloud config, ip address...)
- Join CloudServer vào CloudRing (theo cơ chế join node trong Chord).
- Cập nhật lại vị trí các replica nằm sai vị trí. Di chuyển.
- Trong thời gian di chuyển, những replica cần được di chuyển đánh dấu là
  updated = False và DataObject vẫn sẽ trong trạng thái chưa đồng bộ
  xong. Tuy nhiên, khi đang cập nhật như vậy, có request đến DataObject
  đó. Và các replica đều đang cập nhật. --> Thông báo ng dùng chờ? [bad
  idea].
- Lưu thông tin CloudServer vào database.
- Đầu ra: Thông báo thêm thành công hay không.

##9. Kịch bản Loại bỏ CloudServer.

- Đầu vào: User lựa chọn CloudServer cần loại bỏ khỏi CloudRing.
- Thực hiện Leave CloudRing (Theo cơ chế leave trong Chord).
- Khi 1 CloudServer leave CloudRing, cập nhật các replica trong CloudServer đó
  updated = False. Điều hướng request (nếu có) đến các replica updated = True.
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
