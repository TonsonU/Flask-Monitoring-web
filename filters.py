import pytz
from datetime import datetime

def datetime_bangkok(value, fmt='%Y-%m-%d %H:%M:%S'):
    """
    Filter สำหรับแปลง datetime จาก UTC (หรือค่า tzinfo อื่น ๆ)
    เป็น Asia/Bangkok แล้วค่อย format
    """
    if not value:
        return ''
    if value.tzinfo is None:
        # สมมติว่าเวลาที่ไม่มี tzinfo เป็น UTC
        value = value.replace(tzinfo=pytz.utc)

    bangkok_tz = pytz.timezone('Asia/Bangkok')
    local_dt = value.astimezone(bangkok_tz)
    return local_dt.strftime(fmt)