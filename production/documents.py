from printing.documents import SuzysDocument

def picking_list(production_order_shipment):
    '''create a picking_list for a production_order'''
    production_order = production_order_shipment.production_order
    production_order_items = production_order.productionorderitem_set.all()

    document = SuzysDocument()

    document.add_title('Picking List {}'.format(production_order_shipment))

    document.add_invoice_delivery_headers(
        production_order.invoice_to.printing_address_newlines().replace('\n', '<br></br>'),
        production_order.ship_to.own_address.printing_address_newlines().replace('\n', '<br></br>'))


    table_data = [['sku', 'ean_code', 'qty']]
    [table_data.append([prod.product.sku, prod.product.ean_code, prod.qty]) for prod in production_order_items]
    document.add_table(table_data, [0.33]*3)

    return document.print_document()