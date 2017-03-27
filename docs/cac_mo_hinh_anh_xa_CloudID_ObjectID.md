# Phân tích và lựa chọn mô hình ánh xạ Data Object - Cloud Server cho hệ thống MCS

Một trong những bài toán quan trọng nhất trong hệ thống MCS, đó là bài toán xây dựng cơ chế phân giải tên ( **object naming** - **name resolution**) cho các Data Object lưu trữ trong hệ thống. Nội dung của bài toán này được mô tả thông qua các vấn đề sau:

- Khi người dùng muốn lưu trữ một Data Object có tên là **x** lên hệ thống, Data Object (trên thực tế là các Replica của Data Object) này sẽ được lưu trữ Ở Cloud Server nào ?
- Khi người muốn lấy nội dung của một Data Object **x** thông qua tên của Data Object đó, làm sao để hệ thống phân giải tên của **x** để tìm ra các Replica của **x** đang lưu trữ tại vị trí nào (Cloud Server nào) trên hệ thống?

Bài viết này phân tích và đưa ra một số giải pháp giải quyết bài toán này. Dựa trên các giải pháp này, chúng ta sẽ tiến hành xây dựng các mô hình ánh xạ Data Object - Cloud Server cho hệ thống MCS. Sau đó, chúng ta sẽ so sánh các mô hình với nhau, đồng thời phân tích các ưu điểm và nhược điểm của từng mô hình, từ đó tìm ra mô hình phù hợp nhất cho hệ thống MCS.

## 1. Các phương pháp giải quyết bài toán phân giải tên trong hệ thống MCS

Đầu vào của bài toán phân giải tên, đó là tên của Data Object mà người dùng muốn tương tác. Trong hệ thống, thì tên của một Data Object là tên tuyệt đối và duy nhất. Ví dụ, một Data Object có thể có tên tuyệt đối như sau: **/home/images/images1.png**. Đầu ra của bài toán, đó là địa chỉ truy cập của Cloud Server đang chứa replica của Data Object đó.

Như vậy, chúng ta có thể thấy, về cơ bản mục tiêu của bài toán là xây dựng một ánh xạ đơn ánh **f**, sao cho với một Data Object có tên là **x** được nằm trên Cloud Server có địa chỉ truy cập là **y**, thì **f(x) = y**. Trong hệ thống MCS, **f** được gọi là cơ chế mapping giữa Data Object và Cloud Server.

Chúng ta có nhiều phương pháp để xây dựng cơ chế mapping **f**, trong bài viết này, hai cơ chế sau đây được sử dụng:

- Cơ chế mapping bằng SQLTable(DataObjectID, Cloud\_ServerID)
- Cơ chế mapping bằng DistributedHashTable - DHT

Với mỗi một cơ chế mapping ở trên, chúng ta có thể xây dựng được một hoặc nhiều mô hình ánh xạ Data Object - Cloud Server. Mô hình ánh xạ được hiểu là với một cơ chế mapping **A** cho trước, chúng ta sẽ xây dựng một kiến trúc hệ thống bao gồm các đối tượng cụ thể và cách thức tổ chức, liên kết và phối các đối tượng này để thực thi cơ chế mapping **A** trong hệ thống. Tại thời điểm này, chúng ta đưa ra được 3 mô hình khả thi cho 2 cơ chế mapping phía trên là:

- Mô hình VM Ring with Virtual Machine Node
- Mô hình Cloud Ring with Reference Node
- Mô hình Mapping (CloudID,ObjectID) by SQL Table.

Trong đó, 2 mô hình Cloud Ring with Reference Node và VM Ring with Virtual Machine Node được xây dựng dựa trên cơ chế Distributed Hash Table, còn mô hình Mapping (CloudID,ObjectID) by SQL Table được xây dựng dựa trên cơ chế mapping SQLTable(DataObjectID, Cloud\_ServerID).

Như vậy, mô hình ánh xạ Data Object - Cloud Server là kết quả của việc giải quyết bài toán phân giải tên, và nó là nền tảng để xây dựng hệ thống MCS. Tuy nhiên, việc phân tích bài toán phân giải tên chỉ là bước đầu trong quá trình xây dựng mô hình, và công việc này cho chúng ta một bộ khung cơ bản của hệ thống. Do đó,chúng ta phải tiếp tục hoàn thiện mô hình bằng cách xây dựng các cơ chế xử lý các vấn đề khác trong hệ thống như:

- Cơ chế cân bằng dữ liệu lưu trữ - data balancing giữa các Cloud Server.
- Cơ chế sao lưu - replicate Data Object
- Cơ chế tối ưu hóa hiệu năng hệ thống
- Cơ chế sử dụng Message Queue để time-coupling
- Cơ chế đồng bộ hóa cho các bản sao
- Cơ chế phục hồi các Replica bị lỗi của một Data Object - Replica recovery.
- Cơ chế quản lý thông tin, trạng thái của một Data Object và thông tin, trạng thái của các Replica của Data Object đó.

Trong phần tiếp theo, chúng ta sẽ mô tả chi tiết, và sau đó đi vào xây dựng hoàn thiện 3 mô hình đã được đề xuất.

## 2. Các mô hình ánh xạ Data Object - Cloud Server

### 2.1 Mô hình VM Ring with Virtual Machine Node

#### 2.1.1 Mô hình VM Ring Cơ bản

Mô hình VM Ring with Virtual Machine Node là mô hình được xây dựng dựa trên nền tảng là Chord Protocol, với các Node trên Chord Logic Ring là các Virtual Machine. Mỗi Virtual Machine tham chiếu và đại diện cho một Cloud Server trên hệ thống. Mô hình VM Ring cơ bản được mô tả như sau:

![Virtual_Node_Architech](./images/Virtual_Node_Architect.png)

Quá trình phân giải tên Data Object khi hệ thống sử dụng mô hình Virtual Machine Node diễn ra như sau:

Client sẽ gửi yêu cầu tải về một Data Object có tên là **x** Lên MCS WSGI Server. MCS WSGI Server nhận được request rồi chuyển tiếp request tới một trong các VM Node trên Ring. VM Node này sẽ thực hiện nhiệm vụ Hashing Data Object Name để lấy ra Data\_Object\_ID. Sau đó VM Ring sẽ dựa vào Chord Lookup Protocol để đi tới VM Node là Successor Node của **Data\_Object\_ID** này, Cloud Server được VM Node này đại diện cho chính là Cloud Server chứa Data Object cần tìm. Sau đó VM Node này sẽ gửi trả về cho MCS WSGI Server thông tin của Cloud Server mà nó đang đại diện. MCS WSGI Server gửi thông tin này tới Client, sau đó Client sử dụng thông tin này để kết nối trực tiếp tới Cloud Server để tải về nội dung của Data Object.

#### 2.1.2 Xây dựng cơ chế giải quyết các vấn đề  cân bằng dữ liệu lưu trữ và sao lưu Data Object

Về mặt lý thuyết, khi sử dụng phương pháp Chord Protocol để phân giải tên, thì xác suất một Data Object có tên tuyệt đối là **x** được một Cloud Server lưu trữ là **1/n**. Điều đó có nghĩa là, trong trường hợp tất cả các Cloud Server mà người dùng có có Dung lượng lưu trữ bằng nhau, thì hệ thống có tính chất cân bằng tải. Tuy nhiên, vấn đề xảy ra ở đây là dung lượng của các Cloud Server mà người dùng có thường là rất khác nhau,nên hệ thống chưa thể thực hiện việc phân tán tải một cách lý tưởng. Tính chất phân tán tải lý tưởng được thực hiện khi lượng dữ liệu được lưu trữ trên một Cloud Server tỉ lệ thuận với dung lượng của Cloud Server đó.

Một vấn đề khác mà chúng ta cần xử lý, đó là vấn đề sao lưu các Data Object: Một Data Object trên hệ thống cần được lưu trữ trên **k** Cloud Server (k>=2) để đảm bảo rằng dữ liệu trên hệ thống vẫn an toàn ngay cả khi một Cloud Server nào đó gặp sự cố (Ví dụ như nếu khách hàng có một số Swift Cloud Server đặt tại 1 số thành phố hay mất điện chẳng hạn). Thường k được chọn = 3, tức là khi người dùng tải lên một Data Object, thì chúng ta sẽ tạo ra 3 bản sao của Data Object đó và lưu trữ trên 3 Cloud Server khác nhau.

**Ý kiến của thầy:** Nếu sử dụng mô hình với Node là Virtual Machine này, các thông tin về Object và các thông tin về các Replica của các Object này - Các thông tin chứa trong 2 Table ObjectMetadata và Replica:

![class_diagram.png](./images/class_diagram.png)

sẽ được lưu trữ trên các VM node. Thầy muốn phát triển thêm về mô hình này

### 2.2 Mô hình Cloud Ring with Reference Node

Mô hình Cloud Ring with Reference Node cũng được xây dựng dựa trên nền tảng Chord Protocol, tuy nhiên Ring lúc này là một đối tượng nằm bên trong MCS WSGI Server các Node trên Chord Logic Ring lúc này sẽ là các đối tượng tồn tại bên trong WSGI Server Process.

Khi sử dụng mô hình này, thông tin chứa trên các Node đơn thuần là Địa chỉ của các Cloud Server đang chứa các Replica của Object này.

Quá trình lookup Data Object khi hệ thống sử dụng mô hình Reference Node diễn ra như sau:

Client sẽ gửi yêu cầu tải về một Data Object có tên tuyệt đối  là **x** Lên MCS WSGI Server. MCS WSGI Server nhận được request sẽ thực hiện việc tạo **Data\_Object\_ID = Hashing(Data\_Object\_Name)** rồi thực hiện phương thức lookup từ một trong các Node trên Ring. Reference Node sẽ dựa vào Chord Lookup Protocol để đi tới Reference Node là Successor Node của **Data\_Object\_ID** này, Cloud Server được Reference Node này đại diện cho chính là Cloud Server chứa Data Object cần tìm. Lúc này, Reference Node sẽ trả về cho MCS WSGI Server thông tin của Cloud Server mà nó đang đại diện. MCS WSGI Server gửi thông tin này tới Client, sau đó Client sử dụng thông tin này để kết nối trực tiếp tới Cloud Server để tải về nội dung của Data Object.

![Virtual_Node_Architech](./images/HA_current_architect.png)

### 2.3 Mô hình Mapping (CloudID,ObjectID) by SQL Table

Mô hình Mapping (CloudID,ObjectID) by SQL Table sử dụng một Table trong Cơ sở dữ liệu để lưu trữ ánh xạ (ObjectID,CloudID). Khi chúng ta muốn biết một Data Object có ObjectID là **x** đang ở Cloud Server nào, chúng ta sẽ truy cập vào Table này để tìm ra CloudID tương ứng với ObjectID **x**.

Talble Mapping(CloudID, ObjectID) sẽ có dạng như sau

| ObjectID      | CloudID
| ------------- |:-------------
|1              | 5
|2              | 5
|3              | 4
|...            | ...

Chúng ta sẽ làm rõ hơn về ý (3):

Ý kiến người viết: Trên thực tế, chúng ta có thể vứt cái table ObjectMetadata đi. Thông tin về Object Metadata có thể lưu xuống ReplicaMetadata (Bảng Replica hiện tại)

Trên hệ thống, để quản lý trạng thái một Data Object, chúng ta phải lưu trữ thông tin quản lý của Data Object đó. Khi người dùng muốn lấy về một Data Object từ hệ thống thông qua tham số truyền vào là tên của Data Object, chúng ta phải kiểm tra xem Data Object đó đang ở trạng thái nào. Trong một số trạng thái đặc biệt, chúng ta không thể trả về nội dung của Data Object cho client được ( Ví dụ như khi người dùng nào đó đang cập nhật nội dung của Data Object chẳng hạn.)

**Note:** Theo ý tưởng mới, chúng ta sẽ suy ra thông tin quản lý của Data Object dựa trên thông tin quản lý của các Replica của Data Object đó.

Ví dụ, một Object x có 3 Replica, thì nếu trong 3 replica, 1 replica ở trạng thái UPDATED, 2 replica còn lại ở trạng thái NOT UPDATE thì có nghĩa là Data Object này đang ở trạng thái Replica_Updating  (tức là một số replica đã được cập nhật nội dung mới nhất, một số replica khác thì chưa cập nhật).

(Với điều kiện của hệ thống là tên của các Data Object trên hệ thống là phân biệt với nhau đôi một).

- Làm sao để lưu trữ các thông tin về một Data Object và các thông tin về các Replica của Data Object đó - Data Object Information và Object Replica Information?

## 3. Phân tích và so sánh đặc điểm của các mô hình

