import re
from src.utils.logger import default_logger as logger

NEGATIVE_WORDS = {
    "lỗi", "sai", "chậm", "kém", "tệ", "thất vọng", "khó chịu", "không", "chưa",
    "mất", "hỏng", "hư", "giật", "lag", "đơ", "treo", "crash", "bug",
    "không thể", "không được", "thất bại", "tồi", "dở", "tệ hại"
}

VERY_NEGATIVE_WORDS = {
    "rác", "rất tệ", "quá tệ", "thảm họa", "kinh khủng", "ghê", "vô dụng",
    "lừa đảo", "cướp", "lừa", "scam"
}

POSITIVE_WORDS = {
    "tốt", "hay", "nhanh", "dễ", "tiện", "ok", "ổn", "được", "hài lòng",
    "thích", "đẹp", "xuất sắc", "hoàn hảo", "tuyệt", "ưng"
}

VERY_POSITIVE_WORDS = {
    "rất tốt", "tuyệt vời", "xuất sắc", "hoàn hảo", "tốt nhất", "số 1",
    "tuyệt đỉnh", "amazing", "excellent"
}

MIXED_INDICATORS = ["nhưng", "tuy nhiên", "mặc dù", "song"]

def rule_based_sentiment(text):
    if not text:
        return "Neutral", 0

    text_lower = text.lower()

    very_neg_count = sum(1 for word in VERY_NEGATIVE_WORDS if word in text_lower)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    very_pos_count = sum(1 for word in VERY_POSITIVE_WORDS if word in text_lower)

    has_mixed = any(indicator in text_lower for indicator in MIXED_INDICATORS)

    if has_mixed and (neg_count > 0 or very_neg_count > 0) and (pos_count > 0 or very_pos_count > 0):
        return "Mixed", 0

    total_neg = very_neg_count * 2 + neg_count
    total_pos = very_pos_count * 2 + pos_count

    if very_neg_count > 0 or total_neg >= 3:
        return "Very Negative", -2
    elif total_neg > total_pos:
        return "Negative", -1
    elif very_pos_count > 0 or total_pos >= 3:
        return "Very Positive", 2
    elif total_pos > total_neg:
        return "Positive", 1
    else:
        return "Neutral", 0

def fallback_predict(texts):
    results = [rule_based_sentiment(text) for text in texts]
    labels = [r[0] for r in results]
    scores = [r[1] for r in results]
    logger.info("Using fallback rule-based sentiment")
    return labels, scores
