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

Để bắt đầu việc thiết kế hệ thống SCS, chúng ta đi vào phân tích nhiệm vụ chính của SCS: kết hợp tất cả các Cloud Storage Server của một User thành một kho lưu trữ thống nhất cho user đó.

### Storage Cloud, Data Object và Chord Protocol

Mục đích của việc tạo ra kho lưu trữ thống nhất, đó là cho phép người dùng hệ thống có thể sử dụng hệ thống để lưu trữ các data object hiệu quả mà không cần quan tâm tới việc object được lưu trữ như thế nảo ở hạ tầng lưu trữ bên dưới. Đó là cái nhìn ở góc độ người dùng. Còn ở góc độ người thiết kế hệ thống SCS, chúng ta hiểu rằng, bản chất của việc lưu trữ một Data Object vào hệ thống là việc lưu trữ các bản sao Data Object đó lên các cơ sở dữ liệu mà người dùng sở hữu, và nhiệm vụ của chúng ta là xây dựng các cơ chế để thực hiện công việc lưu trữ này một cách hiệu quả nhất. Các cơ chế được xây dựng để giải quyết các vấn đề sau:

- Khi người dùng tài khoản này muốn lưu trữ một Data Object mới trên hệ thống, hệ thống sẽ sao lưu data Object trên thành bao nhiêu bản, và mỗi bản sao của Data Object trên sẽ được lưu trong Cloud nào trong số các Cloud mà tài khoản sở hữu?
- Khi người dùng tài khoản muốn lấy từ hệ thống về nội dung của một Data Object, làm sao để chúng ta biết chúng ta có thể lấy nội dung Data Object này từ Cloud nào trong số các Cloud của tài khoản? (Lưu ý là một Data Object có nhiều bản sao lưu trên nhiều Cloud Server khác nhau)
- Khi người dùng cập nhật nội dung của một Data Object, làm sao để hệ thống đồng bộ hóa giữa các bản sao của Object đó?
- Khi một Cloud mới được người dùng thêm vào hệ thống, hoặc khi người dùng quyết định loại bỏ một Cloud khỏi hệ thống, chúng ta sẽ thực hiện việc di chuyển dữ liệu giữa các Cloud của người dùng như thế nào?

Xuất phát từ việc giải quyết các vấn đề nêu trên, chúng ta sẽ xây dựng các cơ chế lưu trữ của hệ thống dựa trên nền tảng là một protocol cho phép các hệ thống phân tán lưu trữ, quản lý và truy vấn dữ liệu hiệu quả, đó là **Chord protocol**.

Chord protocol được xây dựng xung xoay quanh 2 đối tượng **Node** và **Value**, và bài toán nền tảng mà Chord Protocol giải quyết là: Cho một đối tượng value **x** và một hệ thống có **n** node, value **x** sẽ được lưu vào node nào trong **n** node trên.

Tại sao chúng ta lại lựa chọn Chord Protocol làm nền tảng để xây dựng các cơ chế lưu trữ của hệ thống ?

#### Lý do lựa chọn Chord protocol

### Xây dựng các cơ chế lưu trữ cho SCS trên nền tảng Chord Protocol

#### Cloud Ring, Cloud Node và Data Object

Áp dụng Chord protocol vào hệ thống của chúng ta:

- Các **Node** trên Ring sẽ là các **Cloud** của User.
- Các **Value** được lưu trữ trên các Node là các **Data Object** mà User cần lưu trữ trên hệ thống.

Để sử dụng Chord Protocol, chúng ta sẽ chọn một **Consistent Hashing** để sinh ID cho các đối tượng trong hệ thống. Consistent Hashing được lựa chọn ở đây là SHA-1, và chúng ta sẽ ký hiệu phương thức Hashing sử dụng SHA-1 là ```SHA1_Hash()```.

Sử dụng Chord Protocol, chúng ta bắt đầu xây dựng các cơ chế xử lý lưu trữ cho hệ thống. Đầu tiên, chúng ta sẽ sử dụng Chord Protocol để xây dựng Chord logic ring - **Cloud Ring**.

#### Init Cloud Ring Process

Để có thể xây dựng Cloud Ring cho một user trong hệ thống, chúng ta cần có thông tin **Cloud\_List**, là một danh sách các **Cloud Object**, để đại diện cho tập các Cloud mà user đó sở hữu. CloudObject chứa thuộc tính **Cloud\_Config** - là thông tin định danh của một Cloud. Thông tin định danh của một Cloud bao gồm: Loại Cloud (S3, SWift, Google Cloud, Ceph,...), thông tin xác thực (account, password, token,...), địa chỉ truy cập của Cloud (Ip Address, Port,...), ... Thông tin này sẽ được sử dụng để tạo ra ID cho Cloud đó.

Quá trình xây dựng Cloud Ring từ tập các Cloud của user diễn ra như sau:

- Đầu tiên chúng ta cần gán cho mỗi một Cloud một định danh **CloudID**. CloudID của một Cloud sinh ra dựa bằng cách sử dụng hàm băm SHA-1 hash thông tin định danh của Cloud đó (IP Address + Account name + Password + Container name...).
- Sau khi tạo ra CloudID cho các Cloud, chúng ta xếp các Cloud lên Cloud Ring, lúc này các Cloud đóng vai trò là các **CloudNode** trong Chord Logic Ring rồi xác định các thông tin định tuyến: Successor Node, Previous Node, Finger Table... cho cho từng Cloud Node trên Cloud Ring theo quy tắc của Chord Protocol. Quá trình sắp xếp các Cloud lên Cloud Ring được thực hiện bằng cách đưa lần lượt các Cloud trong Cloud\_List join vào trong Cloud Ring theo thuận toán **Node\_Join** của Chord Protocol.

##### _Algorithm1: InitCloudRing(Cloud\_List)_

```javascript
function InitCloudRing(Cloud_List){

    // Create CloudID for each Cloud in Cloud List
    for Cloud in Cloud_List:
    {
        Cloud_Identifier_Info = get_identifier_info(Cloud.Cloud_Config);
        Cloud.CloudID = SHA1_hash(Cloud_Indentifier_Info);
    }

    // Init Cloud Ring by first Cloud in Cloud List
    First_Cloud = Cloud_List.get_first_cloud();
    Cloud_Ring = init_cloud_ring(First_Cloud);

    // Put Other Clouds to Cloud Ring by Node Join
    for Cloud in Cloud_List except First_Cloud:
    {
        Cloud.join_node_to_cloud_ring(Cloud_Ring);
    }

    return Cloud_Ring;
}
```

Sau khi xây dụng xong Cloud Ring, chúng ta sẽ lưu thông tin Cloud Ring vào tài khoản User. Bước tiếp theo, chúng ta sẽ xây dựng cơ chế lưu trữ một Data Object lên hệ thống.

#### Create Data Object x in SCS System

Thông tin đầu vào cho quá trình lưu trữ Data Object **x**, đó là tên của Data Object - **x.Object_Name** và nội dung của Data Object **x.Data**. Sử dụng thông tin đầu vào này, việc đầu tiên chúng ta cần làm là giải quyết yêu cầu quan trọng nhất đối với việc lưu trữ Data Object **x** lên hệ thống của chúng ta, đó là: **x** phải được sao lưu thành **k** bản sao (giá trị của **k** sẽ do User thiết lập), và **k** bản sao này và lưu tại **k** Cloud trong số các Cloud mà người dùng có.(\*)

Chúng ta sẽ đáp ứng yêu cầu (\*) bằng cách tạo ra **k** bản sao, mỗi bản sao sẽ có một tên và ID riêng biết. Chúng ta sẽ đặt tên cho các bản sao của **x** bằng cách gán thêm các hậu tố **\_replica(i)** vào tên của x. Ví dụ với Data Object có tên là **data.png** thì các bản sao có thể có tên là **data.png\_replica1**, **data.png\_replica2**, **data.png\_replica3**,... (với k =3)

Lúc này, các replica của **x** sẽ có vai trò như các giá trị **Value** trong hệ thống sử dụng Chord Protocol. Để lưu trữ các replica của **x**, hệ thống sẽ hash tên của các replica (vừa được tạo ra ở bước trước) để tạo thành **replicaID** cho các replica này. Saud đó, cặp \<**replicaID**,**x.Data**\> sẽ tạo thành các **Key-Value** trong hệ thống Chord Protocol. Sau đó, hệ thống SCS sẽ sử dụng Chord Protocol để tìm ra Successor Node tương ứng với **replicaID** của từng cặp \<**replicaID**,**x.Data**\>. Cloud tương ứng với Sucessor Nodeđó sẽ được chọn để lưu trữ cặp \<**replicaID**,**x.Data**\> này.

Sau khi giải quyết yêu cầu (*), chúng ta sẽ xem các vấn đề tiếp theo mà chúng ta phải xử lý khi lưu trữ Data Object **x**:

- Theo yêu cầu (\*), thì Data Object **x** sẽ được sao lưu **k** lần và lưu tại **k** Cloud trên hệ thống. Do vậy, chúng ta cần phải có cách để lưu trữ các ID của các bản sao của x, cũng như trạng thái của các bản sao này (lần cập nhật cuối cùng, trạng thái hiện tại, tốc độ truy cập...)
- Để thực hiện quá trình đồng bộ dữ liệu, chúng ta cần lưu trữ lại danh sách các lần cập nhật gần đây nhất của Data Object **x**, do trong quá trình cập nhật, chỉ có một bản sao trong **k** bản sao được cập nhật, các bản sao khác được cập nhật khi thực hiện đồng bộ. Quá trình đồng bộ sẽ dựa trên danh sách cập nhật này để tiến hành đồng bộ hóa nội dung các bản sao.
- Trong khoảng thời gian từ lúc một bản sao được cập nhật nội dung cho tới khi hệ thống thực hiện việc đồng bộ các bản sao, hệ thống vẫn phải thực hiện việc phản hồi các yêu cầu truy cập tới data Object. Tuy nhiên, trong khoảng thời gian này, nội dung của các bản sao là không giống nhau, vậy hệ thống sẽ trả về cho người dùng nội dung của bản sao nào ? Để giải quyết điều này, chúng ta phải lưu trữ lại bản sao nào được cập nhật cuối cùng. Đây sẽ là bản sao mà hệ thống trả lại cho người dùng.

Chúng ta có thể thấy, để xử lý các vấn đề đã nêu ra, chúng ta phải có cơ chế để lưu trữ các thông tin liên quan tới Data Object x. Giải pháp được sử dụng trong hệ thống SCS, đó là trong quá trình lưu trữ Data Object **x**, đối tượng **Object metadata** sẽ được tạo ra để lưu trữ các thông tin liên quan tới **x**. **Object metadata** của **x** được sử dụng để quản lý các bản sao Data Object **x** cũng như hỗ trợ hệ thống thực hiện các thao tác truy cập, cập nhật và đồng bộ trên **x**. **Object metadata** của **x** chứa các thông tin sau:

- ID của **x**
- Tên của Data Object **x**
- Số lượng các bản sao của x và thông tin về các bản sao của **x**
- Danh sách lịch sử các cập nhật gần đây được thực hiện trên **x**
- Các thông tin khác liên quan tới **x**...

**Object metadata** của x cùng với các bản sao của x là toàn bộ thông tin của Data Object **x** trên hệ thống.


#### Create Data Object Process

Quá trình hệ thống SCS xử lý yêu cầu tạo mới một Data Object có định danh là **x** được diễn ra như sau:

Các thao tác lưu trữ, di chuyển, cập nhật các data object được thực hiện theo các cơ chế được quy định trong Chord protocol.


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

Những thuộc tính trên là đủ để chúng ta lưu trữu thông tin xác thực của tài khoản, và thông tin về các Cloud Storage Server mà tài khoản đó sở hữu. Nhiệm vụ tiếp theo của chúng ta, đó
Trong quá trình thiết kế hệ thống cũng như thiết kế các thành phần trong hệ thống, các đối tượng mà chúng ta xây dựng sẽ liên tục được thay đổi và cập nhật cho đến khi mọi vấn đề trong hệ thống được giải quyết xong.

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
