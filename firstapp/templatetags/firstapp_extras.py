from django import template
import datetime
from django.utils.safestring import mark_safe
import json
register = template.Library()

@register.filter
def compareTwo(value,arg):
    if value==arg:
        return True
    return False

@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))

@register.filter(is_safe=True)
def toUTC(test):
    return test.isoformat()