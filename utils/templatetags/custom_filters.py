from django import template
from django.template.defaultfilters import timesince

register = template.Library()

@register.filter
def vietnamese_timesince(value):
    """Chuyển đổi kết quả timesince sang tiếng Việt"""
    english = timesince(value)
    
    # Thay thế các đơn vị thời gian tiếng Anh sang tiếng Việt
    # Đặt từ số nhiều trước từ số ít để tránh lỗi "phúts"
    translations = {
        'minutes': 'phút',
        'minute': 'phút',
        'hours': 'giờ',
        'hour': 'giờ',
        'days': 'ngày',
        'day': 'ngày',
        'weeks': 'tuần',
        'week': 'tuần',
        'months': 'tháng',
        'month': 'tháng',
        'years': 'năm',
        'year': 'năm',
        'seconds': 'giây',
        'second': 'giây',
        'ago': 'trước',
        ',': ',',
    }
    
    # Thay thế từng từ
    for eng, viet in translations.items():
        english = english.replace(eng, viet)
    
    return english 