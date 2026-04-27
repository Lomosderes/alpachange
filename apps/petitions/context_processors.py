# petitions/context_processors.py

from .models import PromoContent
from .models import Notification

def promo_contents(request):
    left = PromoContent.objects.filter(position='left', is_active=True)
    right = PromoContent.objects.filter(position='right', is_active=True)
    return {
        'promo_items_left': left,
        'promo_items_right': right,
    }

def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}