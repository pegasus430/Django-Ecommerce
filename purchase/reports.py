from printing.documents import SuzysDocument

from .models import *


def purchase_order_report(purchase_order):

    doc = SuzysDocument()

    doc.add_text('Purchase Order for {}'.format(purchase_order.supplier.business_name), 'Title')
    
    delivery_date = purchase_order.est_delivery or 'Unconfirmed'
    po_info = [
        'Our Reference: PO{}'.format(purchase_order.id),
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
        '''
    invoice_to = address_format.format(company=purchase_order.invoice_to).replace('\n', '<br></br>')
    deliver_to = address_format.format(company=purchase_order.ship_to.own_address).replace('\n', '<br></br>')
    doc.add_invoice_delivery_headers(
        invoice_to,
        deliver_to
        )


    doc.add_text('Items requested', 'Heading2')
    items_requested = [
        ['Name', 'sku', 'Quantity']
    ]
    for item in purchase_order.purchaseorderitem_set.all():
        items_requested.append([
            item.material.name,
            item.material.sku_supplier,
            item.qty,
        ])
    doc.add_table(items_requested, [0.4, 0.3, 0.3])

    doc.add_vertical_space(10)
    doc.add_text('Thank you for swift confirmation, communication and delivery.', 'BodyTextCenter')

    return doc.print_document()