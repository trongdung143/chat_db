from datetime import datetime
from langchain.tools import tool, ToolRuntime
from src.core.prompt import business_rule_prompt
from src.core.model import business_rule_model


@tool
def get_time(runtime: ToolRuntime) -> str:
    """
    Trả về thời gian hiện tại của hệ thống.
    Dùng khi cần mốc thời gian hiện tại để phục vụ việc suy luận,
    so sánh với các mốc thời gian khác hoặc trả lời câu hỏi liên quan đến ngày giờ.
    """
    writer = runtime.stream_writer
    writer("INFO:Đang lấy thời gian ...")
    now = datetime.now()
    return f"Thời gian hiện tại là {now.strftime("%Y-%m-%d %H:%M:%S")}"


@tool
async def get_business_rules(topic: str, runtime: ToolRuntime) -> str:
    """
    Lấy thông tin quy tắc nghiệp vụ của hệ thống chương trình thẻ thành viên.

    Tool này dùng để tra cứu các quy định nghiệp vụ liên quan đến:
    - Điều kiện nâng hạng thẻ (SEA, SKY, SUN)
    - Điều kiện duy trì hạng thẻ
    - Quy tắc hạ hạng thẻ
    - Quy định về tài khoản tích lũy
    - Quy định về tour trọn gói
    - Các điều kiện xét hạng dựa trên giá trị giao dịch hoặc số lần sử dụng tour

    Sử dụng tool này khi câu hỏi liên quan đến quy định hoặc lý do nghiệp vụ, ví dụ:
    - Tại sao khách hàng chưa được nâng hạng thẻ?
    - Điều kiện để đạt hạng SKY hoặc SUN là gì?
    - Khi nào khách hàng bị hạ hạng thẻ?
    - Điều kiện duy trì hạng SKY là gì?
    - Khách hàng cần bao nhiêu giá trị giao dịch để lên hạng SUN?

    Args:
        topic: Chủ đề nghiệp vụ cần tra cứu (ví dụ: "điều kiện nâng hạng SKY", "hạ hạng SUN").

    Returns:
        Nội dung quy tắc nghiệp vụ liên quan đến chủ đề để phục vụ phân tích và trả lời.
    """
    writer = runtime.stream_writer
    writer("INFO:Đang phân tích nghiệp vụ ...")
    BUSINESS_RULES = """
    TÀI KHOẢN TÍCH LŨY
    Là tài khoản ghi nhận tổng giá trị tích lũy dịch vụ và số lần sử dụng tour trọn gói
    của khách hàng. Tài khoản này được dùng làm cơ sở để xét nâng hạng, duy trì hạng
    hoặc hạ hạng thẻ thành viên.

    TOUR TRỌN GÓI
    Là chương trình du lịch do Saigontourist tổ chức, bao gồm thời gian chuyến đi,
    điểm đến, các điểm dừng chân, lưu trú, vận chuyển và các dịch vụ khác,
    đã được xác định mức giá trước.

    HẠNG THẺ SEA
    SEA CARD là hạng thẻ tiêu chuẩn dành cho khách hàng mở thẻ để trải nghiệm dịch vụ.

    Điều kiện đăng ký:
    - Khách hàng đăng ký thông tin mở thẻ thành viên.
    - Phát sinh tối thiểu 01 giao dịch dịch vụ bất kỳ.

    Thời hạn duy trì:
    - Không giới hạn thời gian duy trì hạng thẻ (trừ khi có thông báo thay đổi từ Saigontourist).

    HẠNG THẺ SKY
    Điều kiện xét hạng SKY:
    - Tổng giá trị tích lũy >= 50.000.000 VNĐ
    HOẶC
    - Sử dụng tour trọn gói >= 4 lần trong vòng 12 tháng.

    Điều kiện duy trì hạng SKY:
    - Ít nhất 2 lần sử dụng tour trọn gói trong vòng 12 tháng
    HOẶC
    - Tổng giá trị giao dịch >= 30.000.000 VNĐ trong vòng 12 tháng.

    Quy tắc hạ hạng:
    - Trong vòng 12 tháng kể từ ngày đạt hạng SKY, nếu khách hàng
    không đủ điều kiện nâng hạng SUN hoặc không đủ điều kiện duy trì hạng SKY,
    hệ thống sẽ xét hạ xuống hạng SEA.

    HẠNG THẺ SUN
    Điều kiện xét hạng SUN:
    - Tổng giá trị tích lũy >= 100.000.000 VNĐ
    HOẶC
    - Sử dụng tour trọn gói >= 6 lần trong vòng 12 tháng.

    Điều kiện duy trì hạng SUN:
    - Ít nhất 4 lần sử dụng tour trọn gói trong vòng 12 tháng
    HOẶC
    - Tổng giá trị giao dịch >= 60.000.000 VNĐ trong vòng 12 tháng.

    Quy tắc hạ hạng:
    - Trong vòng 12 tháng kể từ ngày đạt hạng SUN, nếu khách hàng
    không đủ điều kiện duy trì hạng SUN thì hệ thống sẽ xét hạ xuống hạng SKY.
    """
    chain = business_rule_prompt | business_rule_model
    try:
        response = await chain.ainvoke(
            {"business_rules": BUSINESS_RULES, "topic": topic}
        )
    except Exception as e:
        return "ERROR:Lấy thông tin nghiệp vụ thất bại!"
    return response.content


tools = [get_time, get_business_rules]
