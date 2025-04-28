from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
# Add this to your existing stroke_extras.py file

@register.filter
def filter_by_status(queryset, status):
    """Filter stroke cases by status"""
    return [case for case in queryset if case.status == status]