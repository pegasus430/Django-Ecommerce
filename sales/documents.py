from printing_tools.documents import SuzysDocument

def picking_list(sales_order_shipment):
    '''create a picking_list for a sales_order'''
    sales_order = sales_order_shipment.sales_order
    sales_order_items = sales_order.salesorderproduct_set.all()

    document = SuzysDocument()

    document.add_title('Picking List {}'.format(sales_order_shipment))

    document.add_invoice_delivery_headers(
        sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
        sales_order.ship_to.printing_address_newlines().replace('\n', '<br></br>'))


    table_data = [['sku', 'ean_code', 'qty']]
    [table_data.append([prod.product.product.sku, prod.product.product.ean_code, prod.qty]) for prod in sales_order_items]
    document.add_table(table_data, [0.33]*3)

    return document.print_document()


def customs_invoice(sales_order_shipment):
    '''create a picking_list for a sales_order'''
    sales_order = sales_order_shipment.sales_order
    sales_order_items = sales_order.salesorderproduct_set.all()

    document = SuzysDocument()

    document.add_title('Commercial Invoice')

    document.add_invoice_delivery_headers(
        sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
        sales_order.ship_to.printing_address_newlines().replace('\n', '<br></br>'))

    '''
    Add invoice info:
    - invoice number
    - invoice date
    '''

    table_data = [['Prodcut', 'SKU', 'Qty', 'Export Code', 'Unit Price', 'Total Price']]
    [table_data.append([prod.product.product.name, prod.product.product.sku, prod.qty, \
            prod.product.product.customs_code_export, prod.unit_price, \
            prod.qty * prod.unit_price]) for prod in sales_order_items]
    document.add_table(table_data, [1.0/len(table_data[0])]*len(table_data[0]))

    return document.print_document()    
