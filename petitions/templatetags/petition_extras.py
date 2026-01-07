# petitions/templatetags/petition_extras.py
from django import template
from petitions.models import Vote

register = template.Library()

@register.filter
def is_voted(user, petition_id):
    return Vote.objects.filter(user=user, petition_id=petition_id).exists()