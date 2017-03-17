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

- Quản lý DataObject: Cho phép người dùng sử dụng hệ thống để lưu trữ và quản lý các DataObject bằng các thao tác như lấy về Object Data, tạo mới, di chuyển, cập nhật, xóa bỏ DataObject. Trong trường hợp Upload, cho người dùng lựa chọn số lượng bản sao của một DataObject, cho phép người dùng lựa chọn một trong 2 chế độ: hoặc người dùng tự xác định Cloud nào sẽ lưu trữ bản sao của DataObject, hoặc hệ thống sẽ tự động lựa chọn các Cloud phù hợp.

- Quản lý CloudNode: Cho phép người dùng cấu hình danh sách các CloudNode mà người dùng có trên hệ thống, cho phép thêm mới và gỡ bỏ các CloudNode khỏi hệ thống. Khi người dùng thực hiện thao tác gỡ bỏ CloudNode khỏi hệ thống, hệ thống cho phép người dùng lựa chọn xem có giữ lại các DataObject đang lưu trữ trên CloudNode đó ( di chuyển các DataObject nằm trên CloudNode bị gỡ bỏ sang các CloudNode còn lại của hệ thống) hay không. Bên cạnh đó, hệ thống cho phép người dùng kiểm tra trạng thái của các CloudNode.

## 3. Thiết kế biểu đồ lớp của hệ thống

Dựa vào tài liệu thiết kế hệ thống đã xây dựng, chúng ta có biểu đồ lớp của hệ thống như sau:

![class_diagram](./images/class_diagram.png)

## 4. Thiết kế cơ chế xử lý các ca sử dụng của người dùng

Trong phần này, chúng ta trình bày các cơ chế được hệ thống sử dụng để xử lý các yêu cầu trong các kịch bản sử dụng của người dùng.

### 4.1 Đăng ký tài khoản

**Kịch bản sử dụng**: Người dùng chưa có tài khoản trên hệ thống truy cập vào trang đăng ký tài khoản.

#### 4.1.1 Input

Thông tin xác thực của tài khoản User.

- User lựa chọn hình thức đăng ký (SignUp with Email, Username & Password hoặc
  Social Authentication).
- Email-User-Password: Người dùng nhập thông tin, sau đó sẽ có email xác thực
  đến địa chỉ email đã đăng ký.
- Social Authentication.

#### 4.1.2 Các bước xử lý

- Hệ thống kiểm tra các thông tin mà User cung cấp có hợp lệ hay không.
- Hệ thống tạo một User mới, và lưu thông tin của User mới vào database.

#### 4.1.3 Output

Kết quả tạo tài khoản. Thành công hay thất bại.

### 4.2 Đăng nhập tài khoản

**Kịch bản sử dụng**: Người dùng truy cập vào trang đăng nhập để đăng nhập vào hệ thống.

#### 4.2.1 Input

Thông tin xác thực của tài khoản User, một trong 3 kiểu thông tin xác thực:

- Social Authentication
- SignUp with Email
- Username & Password

#### 4.2.2 Các bước xử lý

- Hệ thống thực hiện truy vấn đến database để kiểm tra thông tin xác thực mà người dùng cung cấp.

#### 4.2.3 Output

Thông báo cho người dùng đăng nhập thành công và redirect người dùng đến trang Dashboard hoặc hiển thị thông báo khi thất bại.

### 4.3 Khởi tạo các CloudNode cho tài khoản

**Kịch bản sử dụng**: Người dùng đã đăng nhập thành công vào hệ thống, tuy nhiên tại thời điểm tài khoản của người dùng mới được tạo ra, thì tài khoản này chưa chứa một CloudNode nào. Để sử dụng các chức năng của hệ thống, người dùng sẽ nhấn vào lựa chọn: Thêm các CloudNode vào tài khoản... để truy cập vào chức năng khởi tạo các CloudNode cho tài khoản.

#### 4.3.1 Input

Danh sách các **CloudConfig** - là thông tin về CloudNode mà người dùng muốn thêm vào tài khoản. **CloudConfig** chứa các thông tin sau:

- type - Loại CloudNode mà người dùng muốn thêm vào hệ thống, thuộc một trong các loại sau:
    - OpenStack Swift
    - Amazone S3
- authentication: Thông tin xác thực cho CloudNode. Load lên từ file cấu hình.
- ip_address: địa chỉ ip của CloudServer, dựa theo endpoint trong file cấu hình. (Giả lập trường hợp các CloudServer đơn giản, không có nhiều Region)

#### 4.3.2 Các bước xử lý

1. Hệ thống kiểm tra tình trạng của từng CloudNode trong danh sách mà người dùng cung câp, sau đó tiến hành kiểm tra CloudAuthentication của CloudNode đó.
1. Sắp xếp Các CloudNode lên **Chord Logic Ring**, tạo ra Cloud Ring theo thuật toán  **InitCloudRing()** trong tài liệu thiết kế, qua đó thiết lập các thông tin định tuyến trên Cloud Ring của các CloudNode - **node\_route\_information**.
1. Sử dụng các thông tin mà người dùng cung cấp và các thông tin mới đã tạo ra trong Cloud Ring để tạo ra các đối tượng **CloudNode** tương ứng với các CloudNode, sau đó lưu các **CloudNode** vào cơ sở dữ liệu.

#### 4.3.3 Output

Hiển thị trang thông tin chi tiết về các CloudNode đang có trong tài khoản và hiển thị thông báo kết quả cho người dùng (thông qua cơ chế alert Message tương tự như Horizon)

### 4.4 Tạo một DataObject / 1 Folder mới trên hệ thống

**Kịch bản sử dụng**: Khi đang ở giao diện hiển thị một folder nào đó, người dùng chọn năng **"Upload new File..."** trên màn hình hệ thống, hoặc người dùng kéo thả (Drag and Drop) một file vào khu vực nội dung folder(tương tự như Google Drive) (trường hợp kéo thả thì hệ thống sẽ xử lý theo chế độ mặc định, replica k = 3).

#### 4.4.1 Input

- Tên file (DataObject) mới
- Nội dung DataObject
- Số lượng replica của DataObject mới (số lượng replica của DataObject mới nhỏ hơn số lượng CloudNode có trên hệ thống).
- Vị trí lưu trữ các replica của DataObject mới:
    - Mặc định: Hệ thống tự quyết định vị trí của các replica dựa vào thuật toán của hệ thống.
    - Tùy chỉnh: Người dùng quyết định các CloudServer nào trong tài khoản nào sẽ lưu trữ các replica.

#### 4.4.2 Các bước xử lý

1. Hệ thống tạo ra tên thực - tên tuyệt đối (absolute name) của DataObject mới và tạo ra object.id từ tên tuyệt đối này.
1. Hệ thống tìm kiếm xem object.id vừa tạo ra đã có trong hệ thống chưa? Xảy ra 2 trường hợp:
    - Trường hợp 1: object.id chưa có trong hệ thống -> Hệ thống sẽ tiếp tục luồng xử lý.
    - Trường hợp 2: object.id đã có trong hệ thống, tên DataObject này đã tồn tại -> Hệ thống sẽ hỏi xem người dùng có muốn đổi tên cho DataObject mới hay không.
1. Sau khi có tên phù hợp cho DataObject mới, hệ thống tiến hành tạo id cho các replica của DataObject mới. Các bước thực hiện:
    1. Hệ thống kiểm tra option được người dùng lựa chọn là tùy chỉnh hay mặc định, tiến hành chọn các CloudNode sẽ lưu trữ các replica do người dùng tạo ra:
        - Nếu là tủy chỉnh, hệ thống kiểm tra xem các CloudNode người dùng đã chọn có đủ dung lượng lưu trữ hay không ? Nếu không đủ, hệ thống báo lỗi cho người dùng.
        - Nếu là mặc định, hệ thống kiểm tra xem dung lượng lưu trữ ở các CloudNode nào trong số các CloudNode còn đủ, hoặc hash replica_name, hoặc round\_robin để chọn ra các CloudNode phù hợp để lưu trữ các Replica của DataObject mới. (Cái này em xin bàn thêm với thầy và các anh).
    1. Trong trường hợp số lượng CloudNode phù hợp để lưu trữ DataObject mới nhỏ hơn số lượng replica người dùng muốn tạo, hệ thống báo lỗi tới người dùng.
    1. Sau khi chọn được các CloudNode phù hợp, hệ thống tạo ra các replica.id cho các Replica của DataObject mới. Chiến lược tạo ra các replica.id có thể là Hash Replica Name, hoặc sử dụng biến **auto\_increment\_replica.id** trên các CloudNode.
1. Hệ thống sẽ tạo ra các replica sau khi đã có replica.id cho từng replica, sau đó một replica **x** trong số các replica sẽ được lưu lại và đánh dấu **updated**, các replica còn lại sẽ được đánh dấu **not\_updated** (Đánh dấu bằng biến boolean),trong các **Replica**. Sau khi replica **x** đã hoàn tất quá trình lưu dữ liệu của DataObject lên CloudNode,hệ thống tạo ObjectMetadata cho DataObject mới và chuyển trạng thái của DataObject sang **CREATING**, sau đó hệ thống thực hiện 2 công việc sau:
        1. Lưu Object Metadata cũng như các Replica đã tạo ra vào Database.
        1. Đẩy một message chứa thông tin về DataObject mới tạo lên **Create\_Data\_Object\_Queue** trên RabbitMQ Server
1. Cập nhật nội dung Folder chứa DataObject mới. Sau khi tác vụ này thực hiện xong, người dùng đã có thể truy cập vào DataObject mới (mà không cần chờ các replica còn lại của DataObject phải sao lưu vào hệ thống, cũng có nghĩa là DataObject ở trạng thái **CREATING** cũng đã cho phép người dùng truy cập vào nội dung DataObject).
1. Định kỳ sau một khoảng thời gian, tạo một **Create\_Data\_Object Daemon Process**, Daemon Process này lấy tin nhắn trong **Create\_Data\_Object\_Queue**, thực hiện việc lấy nội dung của DataObject tương ứng, sau đó lưu nội dung của DataObject này lên các replica còn lại mà chưa được tạo lên các CloudNode tương ứng, sau đó thực hiện chuyển trạng thái của DataObject sang trạng thái **READY**. Kịch bản thực hiện bước này được mô tả như sau:

![create_data_object_process.png](./images/create_data_object.png)

**(Thầy và các anh xem xử lý như thế này có được không ?)**

#### 4.4.3 Output

Hệ thống thông báo kết quả tạo DataObject mới cho người dùng. Hiển thị File mới trong thư mục, thông báo kết quả tạo DataObject mới qua **alert\_message**.

### 4.5 Tải một Folder (bên trong có nhiều File/Folder con) lên hệ thống

### 4.6 Mở nội dung file - Download file

**Kịch bản sử dụng**: Từ màn hình hệ thống, người dùng chọn vào một file rồi lựa chọn chức năng xem nội dung hoặc tải xuống.

#### 4.6.1 Input

- Tên tuyệt đối của DataObject muốn lấy nội dung về.

#### 4.6.2 Các bước xử lý

1. Hệ thống tạo ra object.id bằng cách hash tên của DataObject mà User cung cấp.
1. Kiểm tra có **ObjectMetadata** nào tương ứng vơi object.id vừa tạo ra tồn tại trong cơ sở dữ liệu hay không ?
1. Lấy ObjectMetadata của Object từ Database ra, kiểm tra **status** của DataObject:
    - Nếu DataObject có status là **UPDATING** hoặc **READY** hoặc **CREATING**, thực hiện việc lấy nội dung DataObject.
    - Nếu DataObject có các status còn lại, tùy theo trạng thái Status của DataObject, thông báo lỗi tới người dùng.
1. Lấy ra ranh sách các Replica tương ứng với DataObject này, chọn một replica trong số các replica có **status** là **updated**.
1. Lấy ra **Cloud Ring** từ User Database
1. Sử dụng phương thức Lookup của Chord với đầu vào là replica.id của replica được chọn, thực hiện việc tìm trên Cloud Ring CloudNode đang lưu trữ replica được chọn.
1. Gửi trả về cho Client **CloudConfig** của CloudNode chứa replica được chọn và **replica.id** của replica này

#### 4.6.3 Output

- Nếu thành công, client dựa vào thông tin mà client gửi về (Cloud Config và replica.id), kết nối trực tiếp tới CloudNode chứa replica của DataObject và lấy về nội dung của DataObject, sau đó hiển thị nội dung lên màn hình hoặc tải xuống nội dung.
- Nếu thất bại, thông báo lỗi tới người dùng.

**Xin ý kiến: Trong lúc quét DataObject/Object Metadata, nếu phát hiện**

### 4.7 Tải xuống một thư mục (khác với xem nội dung thư mục - ở đây là lấy toàn bộ nội dung thư mục về)

Đề xuất giải pháp: tương tự như Google Drive, nén thư mục thành file .rar, sau đó tải xuống.

### 4.8 Cập nhật nội dung của DataObject

Kịch bản: Người dùng truy cập vào màn hình hệ thống, chọn một file trên màn hình ve chọn chức năng **cập nhật nội dung...**, hoặc tải lên một file trùng tên và chọn chế độ **ghi đè**.

#### 4.8.1 Input

- Tên tuyệt đối của DataObject mà người dùng muốn cập nhật.
- Nội dung mới của DataObject.

#### 4.8.2 Các bước xử lý

1. Thực hiện hash tên tuyệt đối của DataObject để tạo ra object.id và lấy ra Object Meatadata tương ứng với object.id này trong Database.
1. Kiểm tra status của DataObject mà người dùng cập nhật:
    - Nếu status = **READY**, cho phép tiến hành cập nhật
    - Nếu status = **UPDATING**, hệ thống thông báo cho người dùng DataObject đang được cập nhật, và hỏi người dùng xem muốn tạo một DataObject mới không?
    - Nếu status nằm trong các trường hợp còn lại, xử lý báo lỗi cho người dùng, ngừng tiến trình cập nhật.
1. Hệ thống kiểm tra số lượng DataObject hiện tại đang chờ cập nhật, nếu số lượng này đã đạt tới giới hạn, thông báo lỗi cho người dùng. (1 vấn đề cần thảo luận : có cần kiểm tra dung lượng của DataObject mới? ) - chỉnh sửa lại Document và biểu đồ lớp, thêm thuộc tính số lượng DataObject đang chờ Update?
1. Nếu DataObject cần cập nhật thỏa mãn các điều kiện cập nhật trên, chúng ta chuyển status của DataObject sang **PRE_UPDATE** rồi đẩy nội dung mới của DataObject xuống một trong các Replica của DataObject. Sau khi đẩy xuống hoàn tất, chuyển status của DataObject sang **UPDATING**, sau đó chuyển status của các replica còn lại chưa được cập nhật của Object sang **NOT\_UPDATED**. Sau đó hệ thống gửi message chứa thông tin về DataObject lên **Is\_Synchronizing\_Content\_Queue** trên RabbitMQ Server

1. Định kỳ sau một khoảng thời gian, tạo một **Update\_Data\_Object Daemon Process**, Daemon Process này lấy tin nhắn trong **Is\_Synchronizing\_Content\_Queue**, sau đó thực hiện việc lấy nội dung của DataObject tương ứng từ một trong các replica có status là UPDATED, sau đó cập nhật nội dung của DataObject này lên các replica đang có status là **NOT\_UPDATED** trên CloudNode tương ứng rồi chuyển status các Replica thực hiện cập nhật xong sang **UPDATED**, sau khi tất cả mọi Replica đã thực hiện cập nhật xong, thực hiện chuyển trạng thái của DataObject sang trạng thái **READY**. Kịch bản thực hiện bước này được mô tả như sau:

![update_data_object_process.png](./images/update_data_object.png)

Lý do mà ở bước 1 phải có 2 trạng thái **PRE_UPDATE** và **UPDATING**, đó là do ở trạng thái **PRE_UPDATE**, hệ thống vẫn chưa cập nhật nội dung mới nhất của DataObject lên bất cứ một replica nào, nên DataObject bị chuyển sang **PRE_UPDATE** để từ chối truy cập trong thời gian một replica trong hệ thống cập nhật nội dung mới nhất. Sau khi đã có ít nhất một replica đã cập nhật lên nội dung mới nhất, hệ thống mới chuyển trạng thái của DataObject sang **UPDATING**, tức là cho phép truy cập trở lại.

### 4.9 Xóa một DataObject khỏi hệ thống

#### 4.9.1 Input:

- File được lựa chọn sẽ xóa.

#### 4.9.2 Các bước thực hiện:

1. Từ id của DataObject (đại diện cho file được chọn), lấy được danh sách các Replica.
2. Từ danh sách các Replica, id của Replica, và CloudRing lookup được các CloudNode chứa Replica đó. Sau đó tiến hành gửi Request DELETE xuống. Tuy nhiên vẫn giữ lại 1 Replica mang tính chất backup, nếu người dùng muốn thay đổi quyết định sau này, Replica này sẽ được xóa sau 30 ngày. 

#### 4.9.3 Output:

1. Thông báo kết quả xóa: thành công hay thất bại.
2. Thông báo sẽ có thư mục backup (Trash) sẽ lưu trữ những file đã được chọn xóa. Sau 30 ngày sẽ xóa vĩnh viễn.

### 4.10 Monitor các CloudNode - Kiểm tra dung lượng lưu trữ

#### 4.10.1 Input

CloudNode muốn kiểm tra dung lượng.

#### 4.10.2 Các bước thực hiện

1. Dựa vào CloudConfig có endpoint và các thông tin xác thực, tiến hành đẩy Request kiểm tra Quota của CloudNode đó.
2. Trả về kết quả cho người dùng dạng biểu đồ tròn.

#### 4.10.3 Output

Kết quả trả về dạng biểu đồ.

### 4.11 Monitor các CloudNode - Kiểm tra status của CloudNode.

#### 4.11.1 Input

CloudNode muốn kiểm tra status.

#### 4.11.2 Các bước xử lý

1. Dựa vào CloudConfig có endpoint, thực hiện PING/TELNET đến CloudNode đó. Đây là phương pháp tối giản chỉ phù hợp
   giả thuyết các CloudNode có kiến trúc đơn giản, mạng không quá phức tạp (Không chia thành Region...)
2. Dựa vào kết quả bước 1, kết hợp với 4.10 (Kiểm tra dung lượng) đưa ra status của CloudNode.

#### 4.11.3 Output

Trang thái của CloudNode.

### 4.12 Thêm mới CloudNode vào CloudRing

### 4.13 Loại bỏ CloudNode khỏi CloudRing

### 4.14 Xóa folder

#### 4.14.1 Input

Folder được lựa chọn sẽ xóa

#### 4.14 Các bước thực hiện

1. 

<!--## 7. Kịch bản Update file.

- Đầu vào: User chọn file muốn update và upload version mới cho file.
- Đưa bản update (filename và content) vào cache queue.
- Nếu đến lượt bản update, dựa vào filename, id tìm ra danh sách replica.
- Lựa chọn replica trong danh sách đó.
- Tiến hành PUT content đến CloudServer chứa replica (Dựa vào CloudRing và chord để
  tìm ra được vị trí của replica). Content mới sẽ thay thế content cũ, replica được
  cập nhật. Chuyển trạng thái của replica về updated = True, các replica khác
  updated = False. Khi có request đến MCS, yêu cầu file này, request sẽ được chuyển
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
  đó. Và các replica đều đang cập nhật. Thông báo ng dùng chờ? [bad
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
- Check health qua API?-->
