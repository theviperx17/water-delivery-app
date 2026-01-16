from django.db import transaction
from django.db.models import Max
from .models import DeliveryRound, Order

@transaction.atomic
def allocate_order_to_round(order: Order, round_id: int) -> Order:
    r = DeliveryRound.objects.select_for_update().get(pk=round_id)
    order.round = r
    if r.status == 'open' and r.used < r.capacity:
        order.status = 'proc'
        order.queue_pos = None
    else:
        order.status = 'queued'
        last = (
            Order.objects.select_for_update()
            .filter(round=r, status='queued')
            .aggregate(m=Max('queue_pos'))['m'] or 0
        )
        order.queue_pos = last + 1
    order.save(update_fields=['round', 'status', 'queue_pos'])
    return order
