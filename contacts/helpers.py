from printing.labels import simple_label_38x90
from defaults.helpers import multiple_files_to_zip_httpresponse

def print_address_label_admin(addresses):
    label_data = {}
    for address in addresses:
        filename = u'{}.pdf'.format(address.business_name)
        text = u'''
            {address.business_name}
            {address.contact_first_name} {address.contact_name}
            {address.address1}
            {address.address2}
            {address.postcode} {address.city}
            {address.country}
            '''.replace('\n', '<br></br>').format(address=address)
        label_data[filename] = simple_label_38x90(text)

    return multiple_files_to_zip_httpresponse(label_data, u'addess_labels')




### admin helpers ###
def print_address_label(modeladmin, request, queryset):
    return print_address_label_admin(queryset)
print_address_label.short_description = 'Print address labels'