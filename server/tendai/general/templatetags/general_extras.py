from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def field(str,index):
    list = str.split(' ')
    return list[index]

