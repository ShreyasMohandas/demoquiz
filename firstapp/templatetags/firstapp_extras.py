from django import template
import datetime
from django.utils.safestring import mark_safe
import json
from firstapp.models import *
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

@register.filter(is_safe=True)
def test_specific_topic(value,arg):
    return Topics.objects.filter(student=value,test=arg)