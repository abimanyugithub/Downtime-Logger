from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_duration(value):
    if not isinstance(value, timedelta):
        return value
    total_seconds = int(value.total_seconds())
    days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute
    return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
