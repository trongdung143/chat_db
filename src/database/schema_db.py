CUSTOMERS_SCHEMA = """
TABLE: Customers
Mô tả:
Bảng lưu thông tin khách hàng trong hệ thống.
Đây là bảng trung tâm dùng để xác định danh tính khách hàng,
tìm kiếm khách hàng và kết nối tới các bảng thẻ thành viên
hoặc lịch sử giao dịch.

PRIMARY KEY:
- Id

COLUMNS:
- Id (uniqueidentifier): Khóa chính của khách hàng. Được dùng để liên kết tới CardCustomers.CustomerId và TransactionHistories.CustomerId.
- Code (varchar): Mã định danh khách hàng trong hệ thống.
- Ho (nvarchar): Họ của khách hàng.
- Ten (nvarchar): Tên của khách hàng.
- DiDong_1 (varchar): Số điện thoại chính của khách hàng. Nhân viên CSKH thường dùng trường này để tìm kiếm khách hàng.
- DiDong_2 (varchar): Số điện thoại phụ của khách hàng (ít sử dụng).
- Email (varchar): Địa chỉ email của khách hàng.
- NgaySinh (date): Ngày sinh của khách hàng.
- GioiTinh (int): Giới tính của khách hàng. 0 = Nữ, 1 = Nam.
- CMND (varchar): Số CMND hoặc CCCD của khách hàng.
- Passport (varchar): Số hộ chiếu của khách hàng.
- DiaChi (nvarchar): Địa chỉ nhà của khách hàng.
- ChiNhanh (nvarchar): Tên chi nhánh quản lý khách hàng này.
- ChiNhanh_Code (varchar): Mã chi nhánh quản lý khách hàng.
- Status (int): Trạng thái khách hàng. Giá trị >= 0 nghĩa là khách hàng đang hoạt động, < 0 nghĩa là khách hàng đã bị xóa mềm khỏi hệ thống.
- HoaMaiTichLuy (decimal): Giá trị hoa mai tích lũy của khách hàng. Trường này không được sử dụng trong logic nâng hạng hoặc hạ hạng thẻ thành viên.

RELATIONS:

- Customers.Id → CardCustomers.CustomerId
- Customers.Id → TransactionHistories.CustomerId
"""


CARDS_SCHEMA = """
TABLE: Cards
Mô tả:
Bảng định nghĩa các loại thẻ thành viên trong hệ thống (SEA, SKY, SUN) và các điều kiện cấp thẻ, duy trì hạng thẻ.

PRIMARY KEY:
- Id

COLUMNS:
- Id (int): Khóa chính của loại thẻ. Giá trị: 1 = SEA, 2 = SKY, 3 = SUN. Dùng để liên kết từ CardCustomers.CardId và CardCustomers.NextCardId.
- Name (nvarchar): Tên loại thẻ thành viên (ví dụ: Thẻ SEA, Thẻ SKY, Thẻ SUN).
- Cap_SoDichVuTu (int): Ngưỡng số dịch vụ tối thiểu cần đạt để được cấp thẻ này.
- Cap_SoDichVuDen (int): Ngưỡng số dịch vụ tối đa của khoảng cấp thẻ.
- Cap_TongGiaTriTu (decimal): Ngưỡng tổng giá trị giao dịch tối thiểu (VNĐ) để được cấp thẻ. Khi giá trị tích lũy >= Cap_TongGiaTriTu thì đủ điều kiện nâng hạng.
- Cap_TongGiaTriDen (decimal): Ngưỡng tổng giá trị giao dịch tối đa của khoảng cấp thẻ.
- DuyTri_SoDichVu (int): Ngưỡng số dịch vụ cần đạt trong mỗi chu kỳ để duy trì hạng thẻ.
- DuyTri_TongGiaTri (decimal): Ngưỡng tổng giá trị giao dịch cần đạt trong mỗi chu kỳ để duy trì hạng thẻ.
- TG_HieuLucThe (int): Thời gian hiệu lực của thẻ, tính bằng năm.
- TG_NhacNho (int): Số ngày hệ thống nhắc nhở trước khi thẻ hết hạn.

RELATIONS:
- Cards.Id → CardCustomers.CardId
- Cards.Id → CardCustomers.NextCardId
"""


CARDS_CUSTOMERS_SCHEMA = """
TABLE: CardCustomers
Mô tả:
Bảng lưu trữ thông tin các thẻ của từng khách hàng, 
bao gồm toàn bộ các thẻ mà khách hàng đã sở hữu trong quá trình sử dụng dịch vụ, 
đồng thời ghi nhận lịch sử thay đổi hạng thẻ (nâng hạng hoặc hạ hạng) theo thời gian.

PRIMARY KEY:
- Id

FOREIGN KEYS:
- CustomerId → Customers.Id
- CardId → Cards.Id
- NextCardId → Cards.Id

COLUMNS:
- Id (int): Khóa chính của thẻ khách hàng. Liên kết CardCustomerHistories.CardCustomerId để tìm chu kỳ tích lũy của thẻ này.
- CustomerId (uniqueidentifier): Khách hàng sở hữu thẻ, liên kết Customers.Id.
- CardId (int): Loại thẻ hiện tại của khách hàng (1 = SEA, 2 = SKY, 3 = SUN).
- NgayHieuLuc (datetime): Ngày bắt đầu hiệu lực thẻ, cũng là mốc bắt đầu chu kỳ tích lũy.
- NgayKetThuc (datetime): Ngày hết hạn thẻ. NULL = chưa xác định hoặc hiệu lực dài hạn.
- NextCardId (int): Loại thẻ kế tiếp khi nâng hạng (ví dụ SEA → SKY). NULL = không thể nâng hạng.
- SoLanGiaHan (int): Số lần thẻ đã được gia hạn.
- AutoUpdate (bit): true = hệ thống tự động nâng/hạ hạng khi đủ điều kiện. false = xử lý thủ công.
- Internal (bit): true = thẻ nội bộ (nhân viên), không dùng trong tính toán nâng/hạ hạng.
- CheckTransaction (int): Cờ đánh dấu đã kiểm tra giao dịch.
- SentEmail (bit): Đã gửi email thông báo thẻ cho khách hay chưa.
- Status (int): 0 = thẻ đang hoạt động. <0 = thẻ đã hủy hoặc đã thay thế. Mỗi khách hàng chỉ có 1 thẻ Status = 0.
- IsUpdate (bit): Cờ nội bộ của tool.
- IsCleanup (bit): Cờ nội bộ của tool.
"""


CARDS_CUSTOMER_HISTORIES_SCHEMA = """
TABLE: CardCustomerHistories
Mô tả:
Bảng lưu lịch sử tích lũy theo từng chu kỳ của thẻ khách hàng.
Mỗi bản ghi đại diện cho một chu kỳ tích lũy của một thẻ thành viên trong một khoảng thời gian xác định.
Dữ liệu trong bảng này được dùng để tính toán việc nâng hạng hoặc hạ hạng thẻ.

PRIMARY KEY:
- Id

FOREIGN KEY:
- CardCustomerId → CardCustomers.Id

COLUMNS:
- Id (int): Khóa chính của bản ghi lịch sử tích lũy.
- CardCustomerId (int): Kết nối tới CardCustomers.Id, xác định chu kỳ tích lũy này thuộc thẻ khách hàng nào.
- TG_Tu (datetime): Ngày bắt đầu chu kỳ tích lũy, thường bằng CardCustomers.NgayHieuLuc.
- TG_Den (datetime): Ngày kết thúc chu kỳ tích lũy, thường bằng CardCustomers.NgayKetThuc. Hệ thống dùng giá trị này để xét hạ hạng khi TG_Den trùng với ngày đánh giá.
- GiaTri (decimal): Tổng giá trị tích lũy (VNĐ) trong chu kỳ. Giá trị này được tính bằng tổng TransactionHistories.SoTien của các giao dịch loại Payment nằm trong khoảng thời gian từ TG_Tu đến TG_Den.
- DichVu (float): Tổng số dịch vụ tích lũy trong chu kỳ. Giá trị này được tính bằng tổng ServiceTypes.TichLuy của các giao dịch tương ứng với loại tour hoặc dịch vụ.
- Type (int): Loại bản ghi tích lũy. 0 = tích lũy thông thường.
- Ended (bit): Trạng thái chu kỳ tích lũy. false = chu kỳ đang hoạt động (chưa kết thúc). true = chu kỳ đã kết thúc.
- Ngay (datetime): Ngày tạo hoặc cập nhật bản ghi lịch sử tích lũy.
"""


TRANSACTION_HISTORIES_SCHEMA = """
TABLE: TransactionHistories
Mô tả:
Bảng lưu lịch sử giao dịch tour của khách hàng, dùng để tính tích lũy nâng/hạ hạng thẻ.

PRIMARY KEY:
- Id

FOREIGN KEYS:
- CustomerId → Customers.Id
- LoaiTour → ServiceTypes.Code

COLUMNS:
- Id (int): Khóa chính.
- MaGd (int): Mã giao dịch gốc từ hệ thống Vetour.
- CustomerId (uniqueidentifier): Khách hàng thực hiện giao dịch, liên kết Customers.Id.
- DichVu_Text (nvarchar): Tên dịch vụ (ví dụ: TOURLEND, TOURLEOB).
- LoaiTour (varchar): Mã loại tour, liên kết ServiceTypes.Code để lấy hệ số tích lũy.
- CodeDoan (nvarchar): Mã đoàn tour, dùng để tránh giao dịch trùng.
- HanhTrinh (nvarchar): Hành trình tour.
- BatDau (datetime): Ngày bắt đầu tour.
- KetThuc (datetime): Ngày kết thúc tour. Dùng xác định chu kỳ tích lũy: NgayHieuLuc <= KetThuc <= NgayKetThuc.
- SoTien (decimal): Giá trị giao dịch (VNĐ). Được cộng vào CardCustomerHistories.GiaTri.
- TrangThai (varchar): Trạng thái thanh toán. Chỉ tính giao dịch khi TrangThai = 'Payment'.
- HuyTour (bit): true = tour đã bị hủy.
- NgayBan (datetime): Ngày bán hoặc ngày nhập giao dịch.
- NguonData (nvarchar): Nguồn dữ liệu (thường là Vetour).
- Status (int): >=0 = hoạt động, <0 = đã xóa mềm.
"""


SERVICE_TYPES_SCHEMA = """
TABLE:ServiceTypes
Mô tả:Bảng định nghĩa loại tour và hệ số tích lũy dịch vụ.

PRIMARY KEY:
-Id

COLUMNS:
-Id(int):Khóa chính.
-Code(varchar):Mã loại tour, liên kết từ TransactionHistories.LoaiTour.
-Name(nvarchar):Tên loại dịch vụ (ví dụ:Du lịch trọn gói,Vé máy bay).
-Category(nvarchar):Phân loại dịch vụ (ví dụ:Package=trọn gói).
-TichLuy(float):Hệ số tích lũy dịch vụ.Mỗi giao dịch loại này cộng thêm giá trị này vào CardCustomerHistories.DichVu.
-Status(int):>=0 hoạt động,<0 đã xóa.
"""


FULL_SCHEMA = (
    CUSTOMERS_SCHEMA
    + "\n\n"
    + CARDS_SCHEMA
    + "\n\n"
    + CARDS_CUSTOMERS_SCHEMA
    + "\n\n"
    + CARDS_CUSTOMER_HISTORIES_SCHEMA
    + "\n\n"
    + TRANSACTION_HISTORIES_SCHEMA
    + "\n\n"
    + SERVICE_TYPES_SCHEMA
)


CUSTOMERS_SAMPLE_DATA = """
{
  "Id": "86C21478-B0B2-4C66-8820-9AC991D44A2C",
  "Code": null,
  "Ho": "KY",
  "Ten": "HENRY TICH",
  "DiDong_1": "0917430827CH?LIÊN",
  "NgaySinh": "1954-12-08",
  "GioiTinh": 1,
  "Email": "kimphung@saigontourist.net",
  "ChiNhanh_Code": "STS",
  "Status": 0,
  "HoaMaiTichLuy": null
}

{
  "Id": "5C0E0771-0CD2-421E-B603-B1A663D24A48",
  "Code": "LSTS0923900061045",
  "Ho": "NGUYỄN CẢNH",
  "Ten": "NHÂN",
  "DiDong_1": "0703684029",
  "NgaySinh": "1994-12-27",
  "GioiTinh": 1,
  "Email": "canhnhan94@gmail.com",
  "CMND": "079094012518",
  "Status": 0,
  "HoaMaiTichLuy": 0
}
"""


CARDS_SAMPLE_DATA = """
{
  "Id": 1,
  "Keyword": "the sea",
  "Name": "Thẻ SEA",
  "Cap_SoDichVuTu": 0,
  "Cap_SoDichVuDen": 0,
  "Cap_TongGiaTriTu": 0,
  "Cap_TongGiaTriDen": 0,
  "DuyTri_SoDichVu": 0,
  "DuyTri_TongGiaTri": 0,
  "Status": 0,
  "TG_HieuLucThe": null,
  "TG_NhacNho": null
}

{
  "Id": 2,
  "Keyword": "the sky",
  "Name": "Thẻ SKY",
  "Cap_SoDichVuTu": 3,
  "Cap_SoDichVuDen": 4,
  "Cap_TongGiaTriTu": 50000000,
  "Cap_TongGiaTriDen": 99999999,
  "DuyTri_SoDichVu": 2,
  "DuyTri_TongGiaTri": 35000000,
  "Status": 0,
  "TG_HieuLucThe": null,
  "TG_NhacNho": null
}

{
  "Id": 3,
  "Keyword": "the sun",
  "Name": "Thẻ SUN",
  "Cap_SoDichVuTu": 5,
  "Cap_SoDichVuDen": 0,
  "Cap_TongGiaTriTu": 100000000,
  "Cap_TongGiaTriDen": 0,
  "DuyTri_SoDichVu": 4,
  "DuyTri_TongGiaTri": 70000000,
  "Status": 0,
  "TG_HieuLucThe": 7.0,
  "TG_NhacNho": null
}
"""

CARDS_CUSTOMERS_SAMPLE_DATA = """
{
  "Id": 101,
  "CustomerId": "5C0E0771-0CD2-421E-B603-B1A663D24A48",
  "CardId": 1,
  "NgayHieuLuc": "2024-01-01 00:00:00",
  "NgayKetThuc": "2028-01-01 00:00:00",
  "NextCardId": 2,
  "AutoUpdate": true,
  "Internal": false,
  "Status": 0
}
"""


CARDS_CUSTOMER_HISTORIES_SAMPLE_DATA = """
{
  "Id": 5001,
  "CardCustomerId": 101,
  "TG_Tu": "2024-01-01 00:00:00",
  "TG_Den": "2025-01-01 00:00:00",
  "GiaTri": 62000000,
  "DichVu": 4,
  "Type": 0,
  "Ended": false
}
"""

TRANSACTION_HISTORIES_SAMPLE_DATA = """
{
  "Id": 9001,
  "MaGd": 123456,
  "CustomerId": "5C0E0771-0CD2-421E-B603-B1A663D24A48",
  "LoaiTour": "PKG01",
  "CodeDoan": "HS230915A",
  "BatDau": "2024-03-10 00:00:00",
  "KetThuc": "2024-03-15 00:00:00",
  "SoTien": 30000000,
  "TrangThai": "Payment",
  "HuyTour": false,
  "Status": 0
}
"""

SERVICE_TYPES_SAMPLE_DATA = """
{
  "Id": 1,
  "Code": "PKG01",
  "Name": "Du lịch trọn gói",
  "Category": "Package",
  "TichLuy": 1,
  "Status": 0
}

{
  "Id": 2,
  "Code": "FLT01",
  "Name": "Vé máy bay",
  "Category": "Flight",
  "TichLuy": 0.5,
  "Status": 0
}
"""

FULL_SCHEMA_SAMPLE_DATA = (
    CUSTOMERS_SCHEMA
    + "\n\n"
    + CUSTOMERS_SAMPLE_DATA
    + "\n\n"
    + CARDS_SCHEMA
    + "\n\n"
    + CARDS_SAMPLE_DATA
    + "\n\n"
    + CARDS_CUSTOMERS_SCHEMA
    + "\n\n"
    + CARDS_CUSTOMERS_SAMPLE_DATA
    + "\n\n"
    + CARDS_CUSTOMER_HISTORIES_SCHEMA
    + "\n\n"
    + CARDS_CUSTOMER_HISTORIES_SAMPLE_DATA
    + "\n\n"
    + TRANSACTION_HISTORIES_SCHEMA
    + "\n\n"
    + TRANSACTION_HISTORIES_SAMPLE_DATA
    + "\n\n"
    + SERVICE_TYPES_SCHEMA
    + "\n\n"
    + SERVICE_TYPES_SAMPLE_DATA
)
