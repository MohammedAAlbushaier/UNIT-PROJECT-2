from .models import Campaign


def active_campaigns(request):
    return {
        'active_campaigns_count': Campaign.objects.filter(is_active=True).count()
    }
