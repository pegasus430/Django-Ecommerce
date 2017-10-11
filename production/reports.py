from printing_tools.documents import SuzysDocument

from .models import *


def production_order_report(production_order):
    doc = SuzysDocument()

    doc.add_text('Production Order for {}'.format(production_order.production_location.own_address.company_name), 'Title')
    
    delivery_date = production_order.est_delivery or 'Unconfirmed'
    po_info = [
        'Our Reference: PR{}'.format(production_order.id),
        'Delivery Date {}'.format(delivery_date),
    ]
    table_widths = [0.5, 0.5]
    doc.add_table([po_info], table_widths, bold_header_row=False, line_under_header_row=False, box_line=True)


    address_format = '''{company.company_name}
        {company.address1}
        {company.address2}
        {company.postcode} {company.city}
        {company.country}
        VAT: {company.vat}
        '''.replace('\n', '<br></br>')
    invoice_to = address_format.format(company=production_order.invoice_to)
    deliver_to = address_format.format(company=production_order.ship_to.own_address)
    doc.add_invoice_delivery_headers(
        invoice_to,
        deliver_to
    )


    doc.add_text('Items requested', 'Heading2')
    items_requested = [
        ['Name', 'sku', 'Quantity']
    ]
    for item in production_order.productionorderitem_set.all():
        items_requested.append([
            item.product.name,
            item.product.sku,
            item.qty,
        ])
    doc.add_table(items_requested, [0.4, 0.3, 0.3])

    doc.add_vertical_space(10)
    doc.add_text('Thank you for swift confirmation, communication and delivery.', 'BodyTextCenter')

    return doc.print_document()