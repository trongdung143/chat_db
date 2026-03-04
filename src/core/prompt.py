from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate

prompt_sql = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Bạn là chuyên gia tạo câu lệnh SQL dựa trên thông tin bảng sau:
            {tables_description}
            
            Quan trọng: 
            1. Cơ sử dữ liệu tôi dùng là SQL Server, hãy đảm bảo câu SQL bạn tạo ra tương thích với SQL Server.
            2. Chỉ được dùng SELECT để truy vấn dữ liệu. Không được phép dùng câu lệnh nào khác như INSERT, UPDATE, DELETE, v.v.
            3. Chỉ trả về câu lệnh SQL trên một dòng, không tạo marker nào khác như ```sql, ---SQL START---, ---SQL END---, v.v. để đánh dấu câu SQL. Chỉ trả về câu SQL thuần túy.
            """,
        ),
        ("human", "{messages}"),
    ]
)
