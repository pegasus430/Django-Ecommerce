from .models import *

from django.core.mail import EmailMessage

from StringIO import StringIO
import csv

def send_purchase_report_simple():
    ''' 
    Send email to sascha@suzys.eu for all items that need ordering
    Information is based upon the value of Product.materials_missing and Product.active
    '''
    mat_set = set()
    mat_detail_list = []
    for product in Product.objects.filter(active=True):
        for mat in product.materials_missing:
            mat_set.add(mat)

    for mat in mat_set:
        mat = Material.objects.get(sku=mat)
        mat_detail_list.append({
            'supplier': mat.supplier,
            'sku': mat.sku_supplier,
            'name': mat.name,
            'unit_purchase': mat.get_unit_purchase_display(),
            'unit_usage': mat.get_unit_usage_display(),
            'unit_usage_in_purchase': mat.unit_usage_in_purchase,
        })

    csv_f = StringIO()
    c = csv.DictWriter(csv_f, delimiter=';', fieldnames=mat_detail_list[0].keys())
    c.writeheader()
    [c.writerow(i) for i in mat_detail_list]

    email = EmailMessage(
        'Rough Order List',
        'Rough csv orderlist in attachment.  Containing {} items'.format(len(mat_set)),
        'sila@suzys.eu',
        ['sascha@suzys.eu'],
    )
    email.attach('orderlist.csv', csv_f.getvalue(), 'text/csv')
    email.send()