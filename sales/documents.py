from printing_tools.documents import SuzysDocument

def picking_list(sales_order_shipment):
    '''create a picking_list for a sales_order'''
    sales_order = sales_order_shipment.sales_order
    sales_order_items = sales_order.salesorderproduct_set.all()

    document = SuzysDocument()

    document.add_title(u'Picking List {}'.format(sales_order_shipment))

    document.add_invoice_delivery_headers(
        sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
        sales_order.ship_to.printing_address_newlines().replace('\n', '<br></br>'))

    table_data = [['sku', 'ean_code', 'qty']]
    [table_data.append([prod.product.product.sku, prod.product.product.ean_code, prod.qty])\
        for prod in sales_order_items]
    document.add_table(table_data, [0.33]*3)

    return document.print_document()


def customs_invoice(sales_order_shipment):
    '''
    create a picking_list for a sales_order.
    Loosly based on: http://www.dhl.co.uk/content/dam/downloads/g0/express/customs_regulations_russia/export_import_guidelines_to_russia.pdf
    '''
    sales_order = sales_order_shipment.sales_order
    sales_order_items = sales_order.salesorderproduct_set.all()

    document = SuzysDocument()

    # 3 copies needed
    for i in range(0,3):
        ## Title
        document.add_title('Commercial Invoice')

        ## Invoice info
        table_data = [[u'Invoice number: {}'.format(sales_order.invoice_number),
            u'Invoice date: {}'.format(sales_order.created_at.strftime('%d/%m/%Y')),
            u'Delivery terms: DAP {}'.format(sales_order.ship_to.city),
            u'Payment terms: {}'.format(sales_order.payment_terms),
            ]]
        document.add_table(table_data, [1.0/len(table_data[0])]*len(table_data[0]), bold_header_row=False, 
            line_under_header_row=False, box_line=True)

        ## Invoice and delivery addresses
        document.add_invoice_delivery_headers(
            sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
            sales_order.ship_to.printing_address_newlines(include_phone=True).replace('\n', '<br></br>'))

        ## Product table
        table_data = [['Product', 'Country of Origin', 'Qty (pieces)', 
            'HS Code', 'Unit Price (EUR)', 'Total Price (EUR)']]
        table_columns_width = [0.3, 0.2, 0.1, 0.25, 0.15]
        for prod in sales_order_items:
            product_name = u'{}, pet {}, art: {}, {}'.format(prod.product.product.name, 
                prod.product.product.product_model.umbrella_product_model.get_product_type_display(),
                prod.product.product.sku,
                prod.product.product.umbrella_product.export_composition_description)
            table_data.append([product_name, prod.product.product.umbrella_product.country_of_origin,\
                prod.qty, prod.product.product.umbrella_product.export_hs_code, prod.unit_price, \
                prod.qty * prod.unit_price])
        table_data.append(['', '', '', '', '', ''])    
        table_data.append(['<b>Total price EUR</b>', sales_order.total_order_value, '', '', '', ''])
        table_data.append(['<b>Freight cost EUR</b>', sales_order.transport_cost, '', '', '', ''])
        table_data.append(['<b>Total for payment EUR</b>', 
            sales_order.total_order_value + sales_order.transport_cost,
            '', '', '', ''])
        # table_data.append(['', '', '', '', '', ''])    
        # table_data.append(['<b>Gross Weight</b>', '', '', '', '', ''])    
        document.add_table(table_data, table_columns_width)

        document.add_page_break()

    return document.print_document()    
