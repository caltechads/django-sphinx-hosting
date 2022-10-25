from typing import Dict

from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('theme/templatetags/breadcrumb.html')
def breadcrumb(title: str, *args, **kwargs) -> Dict[str, str]:
    """
    Returns bootstrap compatible breadrumb.
    """
    url_name = None
    if args:
        url_name = args[0]
        if len(args) == 1:
            url_args = []
        else:
            url_args = args[1:]
    return {
        'title': title,
        'url': reverse(url_name, *url_args, **kwargs) if url_name else None
    }
