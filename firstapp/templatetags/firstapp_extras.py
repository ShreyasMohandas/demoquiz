# from django import template

# register = template.Library()

# @register.filter
# def compareTwo(value,arg):
#     if value==arg:
#         return True
#     return False

from django import template

register = template.Library()

@register.filter
def compareTwo(value,arg):
    if value==arg:
        return True
    return False