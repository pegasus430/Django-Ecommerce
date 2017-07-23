from inventory.models import *
from contacts.models import *
from purchase.models import *

def create():
    StockLocation.objects.create(name='Knokke')
    StockLocation.objects.create(name='Gent')

    Relation.objects.create(business_name='Relation Name')

    OwnAddress.objects.create(
        company_name='test company',
        )

    Material.objects.create(
        sku='92GB2029',
        sku_supplier='AAADDB',
        name='Test Material',
        mat_type='FAB',
        cost_per_usage_unit=9.9,
        unit_usage='ME',
        unit_purchase='RO',
        unit_usage_in_purchase='30',
        est_delivery_time='3 weeks',
        supplier=Relation.objects.last(),
        )
    StockLocationItem.objects.create(
        location=StockLocation.objects.get(name='Knokke'),
        material=Material.objects.get(sku_supplier='AAADDB'),
        quantity_in_stock=200
        )

    PurchaseOrder.objects.create(
        supplier=Relation.objects.last(),
        invoice_to=OwnAddress.objects.last(),
        ship_to=OwnAddress.objects.last(),
        )

