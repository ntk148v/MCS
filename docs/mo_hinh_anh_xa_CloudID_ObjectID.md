# Phân tích và lựa chọn mô hình mapping giữa CloudID và Object

Một trong những bài toán quan trọng nhất trong hệ thống MCS, đó là bài toán xây dựng cơ chế phân giải địa chỉ cho các Data Object lưu trữ trong hệ thống. Một số thể hiện cụ thể của bài toán này là:

- Khi người dùng muốn lưu trữ một Data Object có tên là **x** lên hệ thống, Data Object (trên thực tế là các Replica của Data Object) này sẽ được lưu trữ Ở Cloud Server nào ?
- Khi người muốn lấy nội dung của một Data Object thông qua tên **x** của Data Object đó, làm sao để hệ thống phân giải tên của Data Object để lấy ra được vị trí nào (Cloud Server nào) trên hệ thống đang lưu trữ các Replica của Data Object đó?
- Làm sao để lưu trữ các thông tin quản lý của một Data Object ?(3)

Chúng ta sẽ làm rõ hơn về ý (3):

Ý kiến người viết: Trên thực tế, chúng ta có thể vứt cái table ObjectMetadata đi. Thông tin về Object Metadata có thể lưu xuống ReplicaMetadata (Bảng Replica hiện tại)

Trên hệ thống, để quản lý trạng thái một Data Object, chúng ta phải lưu trữ thông tin quản lý của Data Object đó. Khi người dùng muốn lấy về một Data Object từ hệ thống thông qua tham số truyền vào là tên của Data Object, chúng ta phải kiểm tra xem Data Object đó đang ở trạng thái nào. Trong một số trạng thái đặc biệt, chúng ta không thể trả về nội dung của Data Object cho client được ( Ví dụ như khi người dùng nào đó đang cập nhật nội dung của Data Object chẳng hạn.)

**Note:** Theo ý tưởng mới, chúng ta sẽ suy ra thông tin quản lý của Data Object dựa trên thông tin quản lý của các Replica của Data Object đó.

Ví dụ, một Object x có 3 Replica, thì nếu trong 3 replica, 1 replica ở trạng thái UPDATED, 2 replica còn lại ở trạng thái NOT UPDATE thì có nghĩa là Data Object này đang ở trạng thái Replica_Updating  (tức là một số replica đã được cập nhật nội dung mới nhất, một số replica khác thì chưa cập nhật).

(Với điều kiện của hệ thống là tên của các Data Object trên hệ thống là phân biệt với nhau đôi một).

Bài viết này sẽ giới thiệu và phân tích các mô hình có thể giải quyết bài toán này, sau đó sẽ đưa ra các so sánh giữa các mô hình và đưa ra mô hình phù hợp nhất cho hệ thống MCS.

## 1. Các mô hình khả thi

Hiện tại, nhóm phát triển đưa ra được 3 mô hình khả thi để giải quyết bài toán mapping đã đặt ra: Mô hình VM Ring with Virtual Machine Node, mô hình Cloud Ring with Reference Node, mô hình Mapping (CloudID,ObjectID) by SQL Table.

**Ý kiến của thầy:** Thầy muốn phát triển thêm mô hình Chord Ring với các node trên Ring là **các Replica của các Object**. Các Node - **Object Replica** sẽ chứa 2 thông tin: thông tin của Object - Object Content + Object Metadata (1), và vị trí truy cập của các Replica khác của Object trên hệ thống(2)

### 1.1 Mô hình VM Ring with Virtual Machine Node

Mô hình VM Ring with Virtual Machine Node là mô hình được xây dựng dựa trên nền tảng là Chord Protocol, với các Node trên Chord Logic Ring là Các Virtual Machine. Mỗi Virtual Machine tham chiếu và đại diện cho một Cloud Server trên hệ thống.

![Virtual_Node_Architech](./images/Virtual_Node_Architect.png)

Quá trình lookup Data Object khi hệ thống sử dụng mô hình Virtual Machine Node diễn ra như sau:

Client sẽ gửi yêu cầu tải về một Data Object có tên tuyệt đối  là **x** Lên MCS WSGI Server. MCS WSGI Server nhận được request rồi chuyển tiếp request tới một trong các VM Node trên Ring. VM Node này sẽ thực hiện nhiệm vụ Hashing Data Object Name để lấy ra Data\_Object\_ID. Sau đó VM Ring sẽ dựa vào Chord Lookup Protocol để đi tới VM Node là Successor Node của **Data\_Object\_ID** này, Cloud Server được VM Node này đại diện cho chính là Cloud Server chứa Data Object cần tìm. Sau đó VM Node này sẽ gửi trả về cho MCS WSGI Server thông tin của Cloud Server mà nó đang đại diện. MCS WSGI Server gửi thông tin này tới Client, sau đó Client sử dụng thông tin này để kết nối trực tiếp tới Cloud Server để tải về nội dung của Data Object.

**Ý kiến của thầy:** Nếu sử dụng mô hình với Node là Virtual Machine này, các thông tin về Object và các thông tin về các Replica của các Object này - Các thông tin chứa trong 2 Table ObjectMetadata và Replica:

![class_diagram.png](./images/class_diagram.png)

sẽ được lưu trữ trên các VM node. Thầy muốn phát triển thêm về mô hình này

### 1.2 Mô hình Cloud Ring with Reference Node

Mô hình Cloud Ring with Reference Node cũng được xây dựng dựa trên nền tảng Chord Protocol, tuy nhiên Ring lúc này là một đối tượng nằm bên trong MCS WSGI Server các Node trên Chord Logic Ring lúc này sẽ là các đối tượng tồn tại bên trong WSGI Server Process.

Khi sử dụng mô hình này, thông tin chứa trên các Node đơn thuần là Địa chỉ của các Cloud Server đang chứa các Replica của Object này.

Quá trình lookup Data Object khi hệ thống sử dụng mô hình Reference Node diễn ra như sau:

Client sẽ gửi yêu cầu tải về một Data Object có tên tuyệt đối  là **x** Lên MCS WSGI Server. MCS WSGI Server nhận được request sẽ thực hiện việc tạo **Data\_Object\_ID = Hashing(Data\_Object\_Name)** rồi thực hiện phương thức lookup từ một trong các Node trên Ring. Reference Node sẽ dựa vào Chord Lookup Protocol để đi tới Reference Node là Successor Node của **Data\_Object\_ID** này, Cloud Server được Reference Node này đại diện cho chính là Cloud Server chứa Data Object cần tìm. Lúc này, Reference Node sẽ trả về cho MCS WSGI Server thông tin của Cloud Server mà nó đang đại diện. MCS WSGI Server gửi thông tin này tới Client, sau đó Client sử dụng thông tin này để kết nối trực tiếp tới Cloud Server để tải về nội dung của Data Object.

![Virtual_Node_Architech](./images/HA_current_architect.png)

### 1.3 Mô hình Mapping (CloudID,ObjectID) by SQL Table

Mô hình Mapping (CloudID,ObjectID) by SQL Table sử dụng một Table trong Cơ sở dữ liệu để lưu trữ ánh xạ (ObjectID,CloudID). Khi chúng ta muốn biết một Data Object có ObjectID là **x** đang ở Cloud Server nào, chúng ta sẽ truy cập vào Table này để tìm ra CloudID tương ứng với ObjectID **x**.

Talble Mapping(CloudID, ObjectID) sẽ có dạng như sau

| ObjectID      | CloudID
| ------------- |:-------------
|1              | 5
|2              | 5
|3              | 4
|...            | ...

## 2. Phân tích và so sánh đặc điểm của các mô hình
