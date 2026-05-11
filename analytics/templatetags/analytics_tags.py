from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and return list."""
    return [v.strip() for v in str(value).split(delimiter)]


@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Return percentage of value/total."""
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def grade_color(grade_point):
    """Return CSS color class based on grade point."""
    try:
        gp = float(grade_point)
        if gp >= 9:
            return 'var(--success)'
        elif gp >= 7:
            return 'var(--warning)'
        else:
            return 'var(--danger)'
    except (ValueError, TypeError):
        return 'var(--text-muted)'


@register.filter
def sgpa_badge(sgpa):
    """Return badge class based on SGPA."""
    try:
        s = float(sgpa)
        if s >= 8.5:
            return 'pass'
        elif s >= 6.5:
            return 'orange'
        else:
            return 'fail'
    except (ValueError, TypeError):
        return 'orange'


@register.simple_tag
def pass_pct(pass_count, total):
    """Return pass percentage as string."""
    try:
        return f"{round((int(pass_count) / int(total)) * 100, 1)}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0%"
