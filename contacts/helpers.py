from printing_tools.labels import simple_label_38x90
from defaults.helpers import dynamic_file_httpresponse

from sales.helpers import export_product_datafile
from sales.models import PriceList 

import logging
logger = logging.getLogger(__name__)


def print_address_label_admin(addresses):
    label_data = {}
    for address in addresses:
        filename = u'{}.pdf'.format(address.business_name)
        if address.contact_first_name and address.contact_name:
            name = u'{address.contact_first_name} {address.contact_name}'.format(address=address)
        elif address.contact_first_name:
            name = u'{address.contact_first_name}'.format(address=address)
        else:
            name = u'{address.contact_name}'.format(address=address)

        text = u'''
            {address.business_name}
            {name}
            {address.address1} {address.address2}
            {address.postcode} {address.city}
            {country}
            '''.replace('\n', '<br></br>').format(address=address, 
                country=address.get_country_display(), name=name)
        label_data[filename] = simple_label_38x90(text)

    return dynamic_file_httpresponse(label_data, u'address_labels')


def export_datafile_for_customer_admin(relations):
    exported_files = {}
    for relation in relations:
        pricelist = PriceList.objects.get(currency=relation.currency, 
            customer_type=relation.customer_type)
        exported_files['{}.csv'.format(relation)] = export_product_datafile(pricelist)

    return exported_files


### admin helpers ###
def print_address_label(modeladmin, request, queryset):
    return print_address_label_admin(queryset)
print_address_label.short_description = 'Print address labels'

def export_datafile_for_customer(modeladmin, request, queryset):
    return export_datafile_for_customer_admin(queryset)
export_datafile_for_customer.short_description = 'Print product data-files'