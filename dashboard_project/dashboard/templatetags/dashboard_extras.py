# dashboard/templatetags/dashboard_extras.py

from django import template

register = template.Library()


@register.filter
def split(value, delimiter):
    """Split a string into a list based on the delimiter"""
    return value.split(delimiter)


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    return dictionary.get(key)


@register.filter
def truncate_middle(value, max_length):
    """Truncate a string in the middle, keeping the beginning and end"""
    if len(value) <= max_length:
        return value

    # Calculate how many characters to keep at the start and end
    half_max = max_length // 2
    start = value[:half_max]
    end = value[-half_max:]

    return f"{start}...{end}"


@register.filter
def format_duration(seconds):
    """Format seconds into a human-readable duration"""
    if not seconds:
        return "0s"

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@register.simple_tag
def url_replace(request, field, value):
    """Replace a GET parameter in the current URL"""
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
