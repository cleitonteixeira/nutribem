from .models import *
import datetime
from django.utils import timezone

def refresh_requests():
    requests = Requisicao.objects.filter(
        finalizada=False).order_by('dh_aprovacao')
    for r in requests:
        dh_atual = timezone.now()
        dh_rc_12 = r.dh_aprovacao + datetime.timedelta(hours=12)
        dh_rc_24 = r.dh_aprovacao + datetime.timedelta(hours=24)
        if dh_atual > dh_rc_24:
            r.progress = 3
        elif dh_atual > dh_rc_12:
            r.progress = 2
        else:
            r.progress = 1
        r.save(update_fields=['progress'])