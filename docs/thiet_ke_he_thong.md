# Thiết kế hệ thống Scalable Cloud Storage

## 1. Giới thiệu

Cùng với sự phát triển của công nghệ điện toán đám mây và các công nghệ lưu trữ, một phương thức lưu trữ mới ra đời, đó là phương thức **Object Storage Cloud**. Phương thức này cho phép người dùng lưu trữ các nội dung không cấu trúc - các Object data lên các Cloud server với các ưu điểm so với phương thức lưu trữ dữ liệu truyền thống: Khả năng sao lưu bản sao- replication, tốc độ truy cập dữ liệu, tính chịu lỗi, khả năng scale up - scale down hệ thống lưu trữ... Những ưu điểm trên giúp cho các nền tảng block storage phát triển mạnh mẽ thời gian gần đây như: Amazon S3, Swift, Google Cloud Storage, Azure Blob storage (object storage)...

Sự phát triển của các hệ thống Cloud Object Storage đem đến cho người dùng nhiều lựa chọn hơn, tuy nhiên các như cầu sử dụng đa dạng của người dùng đặt ra một loạt vấn đề mới cho Object Storage Cloud:

- Các Object Storage Cloud không có tính đồng nhất(các API cung cấp cho người dùng khác nhau, định dạng dữ liệu khác nhau, vv...).
- Nhu cầu lưu trữ dữ liệu trên nhiều nền tảng khác nhau của những người dùng có nhiều hệ thống Object Storage Cloud.
- Nhu cầu tương tác, đồng bộ dữ liệu giữa 2 Cloud Object Storage.
- Implement phương thức lưu trữ Object Storage trên nền tảng các phương thức lưu trữ khác ( như Block Storage, File System Storage, ...) và tương tác/ đồng bộ các phương thức lưu trữ này với các phương thức lưu trữ Object Storage.

Xuất phát từ nhu cầu thực tiễn của người dùng, nhóm phát triển quyết định xây dựng một hệ thống cho phép giải quyết các vấn đề đã nêu trên. Hệ thống được xây dựng có tên là: Scalable Cloud Storage (SCS). SCS cho phép kết hợp tất cả các cơ sở lưu trữ mà người dùng đang có thành một kho lưu trữ thống nhất. Kho lưu trữ thống nhất sau khi được xây dựng sẽ cung cấp cho người dùng năng lực lưu trữ của tất cả các đám mây mà người dùng đang có, đồng thời có những tính năng nổi bật sau:

- High-availability
- Scalable
- Fault-tolerance
- Load-balancing
- Redundancy storage

Bên cạnh những tính năng trên, hệ thống SCS đảm bảo các tương tác với dữ liệu của người dùng như lưu trữ, truy cập thay đổi dữ liệu... được thực hiện một cách tối ưu - optimize nhất.

### 1.1 SCS Case Study

Hệ thống SCS phù hợp để giải quyết các trường hợp thực tế sau:

## 2. Scenario - System Environment

Trong phần này, chúng ta sẽ trình bày một kịch bản thực tế được sử dụng để làm cơ sở xuất phát cho việc xây dựng hệ thống SCS:

Một tập đoàn lớn có nhiều công ty con, mỗi một công ty con sở hữu hàng loạt các cơ sở lưu trữ dữ liệu sử dụng nhiều công nghệ lưu trữ khác nhau như như swift, amazon S3, Ceph, Google Cloud Storage, vv... Dữ liệu và các cơ sở lưu trữ của các công ty con là riêng biệt và độc lập với nhau.

Tập đoàn sẽ triển khai hệ thống SCS để thực hiện nhiệm vụ chính của SCS, đó là tích hợp tất cả các cơ sở lưu trữ dữ liệu mà một công ty con đang có thành một cơ sở lưu trữ dữ liệu thống nhất cho công ty con đó. Các yêu cầu khác của tập đoàn đối với hệ thống SCS là:

- Hệ thống được xây dựng phải phục vụ cho cả tập đoàn, tuy nhiên phải đảm các công ty độc lập với nhau.
- Dữ liệu do các công ty đưa lên được phân phối đều trên các cloud của công ty đó.
- Đảm bảo hiệu suất hoạt động của hệ thống là tối ưu.
- Đảm bảo hệ thống được thiết kế theo mô hình high-availability, đáp ứng được một lượng tải lớn.
- Đảm bảo sự an toàn của dữ liệu, kể cả trong trường hợp một số các cơ sở lưu trữ bị hỏng hóc - ngừng hoạt động.

## 3. Thiết kế hệ thống

### Xây dựng mô hình kiến trúc hệ thống

Xuất phát từ mục tiêu đầu tiên của hệ thống SCS, là tích hợp nhiều hệ thống lưu trữ dữ liệu của một người dùng thành một hệ thống lưu trữ thống nhất, chúng ta tiến hành thiết kế mô hình kiến trúc và xác định các thành phần cơ bản của hệ thống lưu trữ thống nhất multi-cloud:

Một cách tổng quát nhất, hệ thống có kiến trúc như sau:

![System Architect](./images/large_view_architect.png)

Mô hình kiến trúc phía trên là mô hình kiến trúc đầy đủ của hệ thống, với đầy đủ các thành phần, cùng với đó là hệ thống SCS được scaling để thể hiện đầy đủ các tính chất của một hệ thống phân tán, và phục vụ cho nhiều người dùng cùng một lúc, với mỗi người dùng có tập các hệ thống lưu trữ độc lập với nhau. Tuy nhiên, sử dụng kiến trúc đầy đủ này để thiết kế hệ thống là không phù hợp, do kiến trúc này quá phức tạp và không tập trung vào nhiệm vụ quan trọng nhất của hệ thống, đó là: Tích hợp các hệ thống lưu trữ của một người dùng thành một cơ sở lưu trữ thống nhất cho người đó. Đặt trọng tâm vào giải quyết nhiệm vụ này, chúng ta sẽ sử dụng mô hình kiến trúc sau để thiết kế hệ thống:

![System Architect](./images/system_architect.png)

Dưới góc nhìn này, hệ thống bao gồm các thành phần chính sau:

- SCS: Hệ thống chính mà chúng ta xây dựng, bao gồm WSGI Server để nhận và xử lý request của người dùng, và các Deamon Process thực hiện các chức năng của hệ thống.
- SQL Database Server: Lưu trữ dữ liệu của hệ thống SCS
- Các cloud: Tập hợp các cơ sở lưu trữ

Như đã giới thiệu, hệ thống của chúng ta được xây dựng để phục vụ cho các User. Vì vậy, đầu tiên chúng ta sẽ xác định thông tin của một User trong hệ thống.

### User Data Object

User Data là Object chứa thông tin về một tài khoản trên hệ thống. Một tài khoản trên hệ thống sẽ cần phải có các thông tin sau:

- User authentication data: Thông tin xác thực của Account ( account name, password, GoogleAuthenticationInformation, Facebook Authentication Infomation...)
- CloudList: Dánh sách các Cloud Server mà account đó sở hữu. Thông tin về một cloud server bao gồm các thành phần sau:
    - Cấu hình của cloud - **Cloud Config**:
        - Cloud Type: Loại cloud (AWS S3, Swift, Google Cloud, Ceph,...)
        - Cloud Authentication: Thông tin định danh, xác thực cũng như địa chỉ truy cập của cloud:
            - Cloud IP Address
            - Cloud Account Name
            - Cloud Account Password
            - Additional Information (Switf Container name, S3 Folder, ...)

Chúng ta đã xây dựng xong đối tượng chứa các thông tin cơ bản của một tài khoản trên hệ thống là thông tin xác thực của tài khoản, và thông tin về các Cloud Server mà tài khoản đó sở hữu. Bây giờ, chúng ta bắt đầu đi vào giải quyết nhiệm vụ chính của hệ thống SCS, đó là kết hợp tất cả các Cloud của một User thành một kho lưu trữ thống nhất.

### Cloud Node, Data Object và Cloud Ring

Mục đích của việc tạo ra kho lưu trữ thống nhất, đó là cho phép người dùng hệ thống có thể sử dụng hệ thống để lưu trữ các data object hiệu quả mà không cần quan tâm tới việc object được lưu trữ như thế nảo ở hạ tầng lưu trữ bên dưới. Đó là cái nhìn ở góc độ người dùng. Còn ở góc độ người thiết kế hệ thống SCS, chúng ta hiểu rằng, bản chất của việc lưu trữ một Data Object vào hệ thống là việc lưu trữ các bản sao Data Object đó lên các cơ sở dữ liệu mà người dùng sở hữu, và nhiệm vụ của chúng ta là xây dựng các cơ chế để thực hiện công việc lưu trữ này một cách hiệu quả nhất. Các cơ chế được xây dựng để giải quyết các vấn đề sau:

- Khi người dùng tài khoản này muốn lưu trữ một Data Object mới trên hệ thống, hệ thống sẽ sao lưu data Object trên thành bao nhiêu bản, và mỗi bản sao của Data Object trên sẽ được lưu trong Cloud nào trong số các Cloud mà tài khoản sở hữu?
- Khi người dùng tài khoản muốn lấy từ hệ thống về nội dung của một Data Object, làm sao để chúng ta biết chúng ta có thể lấy nội dung Data Object này từ Cloud nào trong số các Cloud của tài khoản? (Lưu ý là một Data Object có nhiều bản sao lưu trên nhiều Cloud Server khác nhau)
- Khi người dùng cập nhật nội dung của một Data Object, làm sao để hệ thống đồng bộ hóa giữa các bản sao của Object đó?
- Khi một Cloud mới được người dùng thêm vào hệ thống, hoặc khi người dùng quyết định loại bỏ một Cloud khỏi hệ thống, chúng ta sẽ thực hiện việc di chuyển dữ liệu giữa các Cloud của người dùng như thế nào?

Xuất phát từ việc giải quyết các vấn đề nêu trên, chúng ta sẽ xây dựng các cơ chế lưu trữ của hệ thống dựa trên nền tảng là một protocol cho phép các hệ thống phân tán lưu trữ, quản lý và truy vấn dữ liệu hiệu quả, đó là **Chord protocol**.

Chord protocol được sử dụng để thực hiện công việc sau: Cho một đối tượng value **x** và **n** node, Chord sẽ tạo một ID cho **x**, sau đó lưu **x** vào một trong **n** node trên theo Chord protocol. Áp dụng Chord protocol vào hệ thống của chúng ta:

- Các **Node** trên Ring sẽ là các **Cloud** của User.
- Các **Value** được lưu trữ trên các Node là các **Data Object** mà User cần lưu trữ trên hệ thống.

Tại sao chúng ta lại lựa chọn Chord Protocol làm nền tảng để xây dựng các cơ chế lưu trữ của hệ thống ?

#### Reason to chose Chord

Chúng ta bắt đầu đi xây dựng các cơ chế lưu trữ cho hệ thống SCS.
Cơ chế đầu tiên là xây dựng Chord logic ring - Cloud Ring cho một tài khoản mới được tạo ra trên hệ thống.

#### Init Cloud Ring Process

Trong quá trình khởi tạo account **x** trên hệ thống, chúng ta cần thực hiện công việc tạo ra Cloud Ring và update các **Cloud Node Information** cho account **x**. Sử dụng các thông tin định danh của các Cloud chứa trong Cloud List, quá trình **Init Cloud Ring Process** diễn ra như sau:

Các Cloud sẽ được gán các ID, ID của một Cloud sinh ra dựa bằng cách sử dụng hàm băm SHA-1 hash thông tin định danh của Cloud đó. (ta sẽ kỹ hiệu hành động sử dụng hàm băm SHA-1 để sinh ID cho một chuỗi **x** đó là ```Hash```).

- Tạo ra Cloud ID cho các Cloud bằng cách ```Hash``` thông tin định danh(IP Address + Account name + Password + Container name...) lưu trong Cloud Config của cloud đó.
- Sau khi tạo ra Cloud ID cho các Cloud, xếp các Cloud ID này lên Chord Logic Ring, xác định Successor Node, Previous Node, Finger Table... cho các Cloud Node theo quy tắc của Chord Protocol
- Lưu các thông tin được vừa được tạo ra vào **Cloud Node Information** của **Cloud Object** tương ứng.

#### _Algorithm 1: Create Account_

    1. Thông tin của Cloud trên Cloud Ring - **Cloud Node Information**:
        - Cloud ID: ID trên Ring của cloud.
        - Successor Node, Previous Node.
        - Finger Table
        - Additional Informations....

```python
class UserData:
    attr UserAuthenticationData
    attr List<CloudObjet>


class CloudObject:

    attr CloudConfig:
        attr CloudType
        attr CloudAuthentication:
            attr IPAddress
            attr CloudAccountName
            attr CloudAccountPassword
            ...

    attr CloudNodeInformation:
        attr CloudID
        attr SuccessorNode
        attr PreviousNode
        attr FingerTable
        ...
```

Ở đây ta thấy có sự xuất hiện của các khái niệm **Cloud Ring** và **Cloud Node**. Ý nghĩa của chúng là gì? Phần tiếp theo sẽ giải đáp ý nghĩa của các khái niệm này.
```python

def CreateAccount(User_Authentication, Cloud_Information_List):

    # Validate User Authentication and Cloud Authentication
    Validate(User_Authentication)
    for Cloud_Information in Cloud_Information_List:
        Validate_Cloud_Authentication(Cloud_Information)

    Cloud_List = []
    ##
    # Create Cloud Object for each Cloud in User's Cloud List
    for Cloud_Information in Cloud_Information_List:


```

#### Create Data Object

Để lưu trữ một Data Object **x**, đầu tiên hệ thống sẽ hash tên của các data Object để tạo thành ID cho Data Object x, tạo thành các cặp key-value lưu trữ trên các node - các cloud. Một data object có thể được sao lưu ra **x** bản sao, mỗi bản sao sẽ có một key riêng, và sẽ được đẩy vào **x** node - **x** cloud khác nhau.

Các thao tác lưu trữ, di chuyển, cập nhật các data object được thực hiện theo các cơ chế được quy định trong Chord protocol.

Để quản lý các bản sao của một data object và thực hiện các thao tác truy cập, sửa đổi trên các bản sao cũng như thực hiện đồng bộ các bản sao với nhau, thì khi xử lý lưu trữ một **data object**, hệ thống sẽ tạo ra một **object metadata** tương ứng với data object này. Object metadata của Data Object **k** chứa các thông tin sau:

- Danh sách các key của các bản sao của **k**
- Danh sách lịch sử các sửa đổi gần nhất lên các bản sao của **k**

#### Create Data Object Process

Quá trình hệ thống SCS xử lý yêu cầu tạo mới một Data Object có định danh là **x** được diễn ra như sau:


