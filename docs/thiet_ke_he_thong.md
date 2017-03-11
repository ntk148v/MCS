# Thiết kế hệ thống Scalable Cloud Storage

## 1. Giới thiệu

Hệ thống Scalable Cloud Storage (viết tắt: SCS) là hệ thống tích hợp lưu trữ object data trên nền tảng multi-cloud, cho phép người dùng lưu trữ object data đồng thời trên nhiều đám mây. SCS kết hợp tất cả các đám mây mà người dùng đang có thành một kho lưu trữ thống nhất. Kho lưu trữ thống nhất sau khi được xây dựng sẽ cung cấp cho người dùng năng lực lưu trữ của tất cả các đám mây mà người dùng đang có, đồng thời có những tính năng nổi bật sau:

- High-availability
- Scalable
- Fault-tolerance
- Load-balancing
- Redundancy storage

Bên cạnh những tính năng trên, hệ thống SCS đảm bảo các tương tác với dữ liệu của người dùng như lưu trữ, truy cập thay đổi dữ liệu... được thực hiện một cách tối ưu - optimize nhất.

## 2. Scenario - System Environment

Hệ thống ra đời bắt đầu từ bài toán sau:

Một tập đoàn lớn có nhiều công ty con, mỗi một công ty con sở hữu hàng loạt các cơ sở lưu trữ dữ liệu sử dụng nhiều công nghệ lưu trữ khác nhau như như swift, amazon S3, Ceph, Google File System, vv... Dữ liệu và các cơ sở lưu trữ của các công ty con là riêng biệt và độc lập với nhau.

Chúng ta cần phải thiết kế một hệ thống phục vụ cho tập đoàn trên. Yêu cầu được tập đoàn đưa ra là:

- Hệ thống được xây dựng phải phục vụ cho cả tập đoàn, tuy nhiên phải đảm các công ty độc lập với nhau.
- Dữ liệu do các công ty đưa lên được phân phối đều trên các cloud của công ty đó.
- Đảm bảo hiệu suất hoạt động của hệ thống là tối ưu.
- Đảm bảo hệ thống được thiết kế theo mô hình high-availability, đáp ứng được một lượng tải lớn.

## 3. Thiết kế hệ thống

Với các yêu cầu đã đặt ta, chúng ta sẽ thiết kế mô hình chung của hệ thống:

![System Architect](./images/system_architect.png)

Hệ thống bao gồm 3 thành phần chính sau:

- SCS: Hệ thống chính mà chúng ta xây dựng, bao gồm WSGI Server để nhận và xử lý request của người dùng, và các Deamon Process thực hiện các chức năng của hệ thống.
- SQL Database Server: Cơ sở dữ liệu của SCS, chứa thông tin về User sử dụng hệ thống.
- Cloud List: Các Cloud có trong một Account được SCS quản lý, lưu trữ các Data Object của Account đó.

Như đã giới thiệu, hệ thống của chúng ta được xây dựng để đồng thời phục vụ cho nhiều User. Vì vậy, đầu tiên chúng ta sẽ xác định thông tin của một User trong hệ thống.

### User Data Object

User Data là một Object chứa thông tin về một tài khoản trên hệ thống. Object này chứa các thông tin sau:

- User authentication data: Thông tin xác thực của Account ( account name, password, GoogleAuthenticationInformation, Facebook Authentication Infomation...)
- CloudList: Là một danh sách các **Cloud Object** chứa thông tin về các Cloud được account này sử dụng. Một Cloud Object trong CloudList chứa 2 thông tin sau:
    1. Cấu hình của cloud - **Cloud Config**:
        - Cloud Type: Loại cloud (AWS S3, Swift, Google Cloud, Ceph,...)
        - Cloud Authentication: Thông tin định danh, xác thực cho cloud:
        - Cloud IP Address
        - Cloud Account Name
        - Cloud Account Password
        - Additional Information (Switf Container name, S3 Folder, ...)
    1. Thông tin của Cloud trên Cloud Ring - **Cloud Node Information**:
        - Cloud ID: ID trên Ring của cloud.
        - Successor Node, Previous Node.
        - Finger Table
        - Additional Informations....

Ý nghĩa của **Cloud Node Information** cũng như **Cloud Ring** sẽ được trình bày trong phần dưới đây

### Cloud, Data Object và Cloud Ring

Mục đích của việc xây dựng hệ thống SCS, đó là sử dụng SCS để kết hợp tất cả các Cloud của một User thành một kho lưu trữ thống nhất. Hai đối tượng quan trọng nhất trong hệ thống của chúng ta là Data Object và Cloud, tương ứng với 2 đối tượng này nhiệm vụ chính của hệ thống, đó là: Cho một Data Object **k**, tìm các Cloud phù hợp để lưu trữ các bản sao của **k**. Để thực hiện được điều này, chúng ta sử dụng giao thức **Chord protocol**.

Chord protocol được sử dụng để thực hiện công việc sau: Cho một đối tượng value **x** và **n** node, Chord sẽ tạo một ID cho **x**, sau đố lưu **x** vào một trong **n** node trên theo Chord protocol. Áp dụng Chord protocol vào hệ thống của chúng ta:

- Các **Node** trên Ring sẽ là các **Cloud** của User.
- Các **Value** được lưu trữ trên các Node là các **Data Object** mà User cần lưu trữ trên hệ thống.

Các Cloud sẽ được gán các ID, ID của một Cloud sinh ra dựa bằng cách sử dụng hàm băm SHA-1 hash thông tin định danh của Cloud đó. (ta sẽ kỹ hiệu hành động sử dụng hàm băm SHA-1 để sinh ID cho một chuỗi **x** đó là ```Hash```).

#### Init Cloud Ring Process

Trong quá trình tạo mới một account **x** trên hệ thống, công việc tạo ra Cloud Ring cũng như update các **Cloud Node Information** cho account **x** được thực hiện. Sử dụng các thông tin định danh của các Cloud chứa trong Cloud List, quá trình **Init Cloud Ring Process** diễn ra như sau:

- Tạo ra Cloud ID cho các Cloud bằng cách ```Hash``` thông tin định danh(IP Address + Account name + Password + Container name...) lưu trong Cloud Config của cloud đó.
- Sau khi tạo ra Cloud ID cho các Cloud, xếp các Cloud ID này lên Chord Logic Ring, xác định Successor Node, Previous Node, Finger Table... cho các Cloud Node theo quy tắc của Chord Protocol
- Lưu các thông tin được vừa được tạo ra vào **Cloud Node Information** của **Cloud Object** tương ứng.

### Create Data Object

Để lưu trữ một Data Object **x**, đầu tiên hệ thống sẽ hash tên của các data Object để tạo thành ID cho Data Object x, tạo thành các cặp key-value lưu trữ trên các node - các cloud. Một data object có thể được sao lưu ra **x** bản sao, mỗi bản sao sẽ có một key riêng, và sẽ được đẩy vào **x** node - **x** cloud khác nhau.

Các thao tác lưu trữ, di chuyển, cập nhật các data object được thực hiện theo các cơ chế được quy định trong Chord protocol.

Để quản lý các bản sao của một data object và thực hiện các thao tác truy cập, sửa đổi trên các bản sao cũng như thực hiện đồng bộ các bản sao với nhau, thì khi xử lý lưu trữ một **data object**, hệ thống sẽ tạo ra một **object metadata** tương ứng với data object này. Object metadata của Data Object **k** chứa các thông tin sau:

- Danh sách các key của các bản sao của **k**
- Danh sách lịch sử các sửa đổi gần nhất lên các bản sao của **k**

#### Create Data Object Process

Quá trình hệ thống SCS xử lý yêu cầu tạo mới một Data Object có định danh là **x** được diễn ra như sau:

Tạo 
