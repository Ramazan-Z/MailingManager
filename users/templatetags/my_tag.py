from django import template

register = template.Library()


@register.filter()
def media_filter(path: str) -> str:
    """Возвращает путь к аватару пользователя"""
    if path:
        return f"/media/{path}"
    return "/media/avatars/unnamed.jpg"
