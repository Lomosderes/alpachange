from django import template

register = template.Library()

@register.filter
def is_video(url):
    if not url:
        return False

    return url.lower().endswith(('.mp4', '.webm'))
