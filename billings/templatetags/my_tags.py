from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def has_group(context, group_name):
    user = getattr(context.request, 'user', None)
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()