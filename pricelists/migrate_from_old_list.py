from sales.models import OldPriceList, OldPriceListItem, OldPriceTransport
from .models import PriceList, PriceListItem, PriceTransport 

def copy_data():
    ## copy PriceLists
    for old_pr in OldPriceList.objects.all():
        new_pr = PriceList.objects.create(
            status=old_pr.status,
            currency=old_pr.currency,
            customer_type=old_pr.customer_type,
            country=old_pr.country,
            is_default=old_pr.is_default,
            reference=old_pr.reference,
            remarks=old_pr.remarks,
            pk=old_pr.pk
            )
        
        ## copy items
        for old_item in old_pr.oldpricelistitem_set.all():
            new_item = PriceListItem.objects.create(
                price_list=new_pr,
                product=old_item.product,
                rrp=old_item.rrp,
                per_1=old_item.per_1,
                per_6=old_item.per_6,
                per_12=old_item.per_12,
                per_48=old_item.per_48,
                pk=old_item.pk
                )
        
        ## copy transport
        for old_tr in old_pr.oldpricetransport_set.all():
            new_tr = PriceTransport.objects.create(
                country=old_tr.country,
                order_from_price=old_tr.order_from_price,
                shipping_price=old_tr.shipping_price,
                price_list=new_pr,
                pk=old_tr.pk
                )