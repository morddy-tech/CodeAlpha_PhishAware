from django import template

register = template.Library()


@register.filter
def dict_key(value, key):
    """Return the value for a dict key (used for accessing dicts by pk in templates)."""
    try:
        return value.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def display_ratio(value, arg):
    """Render score/percentage with a helpful qualifier."""
    try:
        value = int(value)
        threshold = int(arg)
    except (TypeError, ValueError):
        return "—"
    if value >= threshold:
        return f"Passed ({value}%)"
    return f"Needs review ({value}%)"


@register.filter
def ring_dash(value):
    """SVG circle stroke-dasharray for a r=66 circle (circumference ~414.69)."""
    try:
        score = max(0, min(100, int(value)))
    except (TypeError, ValueError):
        score = 0
    length = round(score * 4.1469, 1)
    return f"{length} 414.7"