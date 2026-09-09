"""Rule-based threshold evaluation for vital signs.

Ngưỡng tham khảo từ tài liệu trong rag/knowledge_base — dùng cho MỤC ĐÍCH SÀNG LỌC,
không thay thế chẩn đoán y khoa chuyên môn.
"""
from typing import Optional, List, Dict

SEVERITY_ORDER = ["normal", "info", "warning", "danger"]


def _rank(severity: str) -> int:
    return SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else 0


def evaluate_blood_pressure(systolic: Optional[int], diastolic: Optional[int]) -> Optional[Dict]:
    if systolic is None or diastolic is None:
        return None
    if systolic >= 180 or diastolic >= 120:
        return {"metric": "blood_pressure", "severity": "danger",
                "message": "Huyết áp ở mức nguy hiểm (cơn tăng huyết áp) - cần đến cơ sở y tế ngay."}
    if systolic >= 160 or diastolic >= 100:
        return {"metric": "blood_pressure", "severity": "warning",
                "message": "Tăng huyết áp độ 2 - nên khám bác sĩ sớm."}
    if systolic >= 140 or diastolic >= 90:
        return {"metric": "blood_pressure", "severity": "warning",
                "message": "Tăng huyết áp độ 1 - cần theo dõi sát và đi khám."}
    if systolic >= 120 or diastolic >= 80:
        return {"metric": "blood_pressure", "severity": "info",
                "message": "Tiền tăng huyết áp - nên điều chỉnh lối sống và theo dõi thêm."}
    return {"metric": "blood_pressure", "severity": "normal", "message": "Huyết áp trong ngưỡng bình thường."}


def evaluate_glucose(glucose: Optional[float], fasting: bool = True) -> Optional[Dict]:
    if glucose is None:
        return None
    if glucose < 54:
        return {"metric": "glucose", "severity": "danger",
                "message": "Hạ đường huyết nghiêm trọng - cần xử trí ngay và liên hệ y tế."}
    if glucose < 70:
        return {"metric": "glucose", "severity": "warning",
                "message": "Hạ đường huyết - cần theo dõi sát, cho ăn/uống đường."}
    if glucose >= 300:
        return {"metric": "glucose", "severity": "danger",
                "message": "Đường huyết rất cao - nguy cơ biến chứng cấp, cần đến cơ sở y tế ngay."}
    if fasting and glucose >= 126:
        return {"metric": "glucose", "severity": "warning",
                "message": "Đường huyết đói cao, nghi ngờ đái tháo đường - nên khám chuyên khoa."}
    if fasting and glucose >= 100:
        return {"metric": "glucose", "severity": "info",
                "message": "Tiền đái tháo đường - cần theo dõi và điều chỉnh chế độ ăn."}
    return {"metric": "glucose", "severity": "normal", "message": "Đường huyết trong ngưỡng bình thường."}


def evaluate_heart_rate(hr: Optional[int]) -> Optional[Dict]:
    if hr is None:
        return None
    if hr < 50 or hr > 130:
        return {"metric": "heart_rate", "severity": "danger",
                "message": "Nhịp tim bất thường nghiêm trọng - cần được khám ngay."}
    if hr < 60 or hr > 100:
        return {"metric": "heart_rate", "severity": "warning",
                "message": "Nhịp tim ngoài ngưỡng bình thường - nên theo dõi thêm."}
    return {"metric": "heart_rate", "severity": "normal", "message": "Nhịp tim bình thường."}


def evaluate_all(systolic=None, diastolic=None, glucose=None, heart_rate=None) -> List[Dict]:
    checks = [
        evaluate_blood_pressure(systolic, diastolic),
        evaluate_glucose(glucose),
        evaluate_heart_rate(heart_rate),
    ]
    return [c for c in checks if c is not None]


def worst_severity(alerts: List[Dict]) -> str:
    if not alerts:
        return "normal"
    return max((a["severity"] for a in alerts), key=_rank)
