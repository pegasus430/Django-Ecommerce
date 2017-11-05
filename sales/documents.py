from printing_tools.documents import SuzysDocument

from .models import *

def picking_list(sales_order_shipment):
    '''create a picking_list for a sales_order, and include tracking-urls of available'''
    sales_order = sales_order_shipment.sales_order
    sales_order_shipment_items = sales_order_shipment.salesorderdeliveryitem_set.all()

    document = SuzysDocument()

    document.add_title(u'Picking List {}'.format(sales_order_shipment))

    document.add_invoice_delivery_headers(
        sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
        sales_order.ship_to.printing_address_newlines().replace('\n', '<br></br>'))

    document.add_heading('Items')
    table_data = [['sku', 'ean_code', 'qty']]
    for prod in sales_order_shipment_items:
        sold_item = prod.sales_order_delivery.sales_order.salesorderproduct_set.get(
            price_list_item__product=prod.product)
        table_data.append([prod.product.sku, prod.product.ean_code, prod.qty])

    document.add_table(table_data, [0.33]*3)

    
    try:
        tracking_ids_raw = sales_order_shipment.request_sprintpack_order_status['TrackIDs']['Package']
        tracking_ids = set()
        try:
            for t_id in tracking_ids_raw:
                tracking_ids.add((t_id['TrackAndTraceURL'], t_id['TrackID']))
        except TypeError:
            tracking_ids.add((tracking_ids_raw['TrackAndTraceURL'], tracking_ids_raw['TrackID']))


        if len(tracking_ids) > 0:
            document.add_vertical_space(10)
            document.add_heading('Tracking information')
            for t_id in tracking_ids:
                if t_id[0] is not None:
                    document.add_paragraph('''Tracking ID: {id}
                        <link href="{link}">{link}</link>'''.format(id=t_id[1], link=t_id[0]))
    except (TypeError, KeyError):
        pass  ## No tracking data known


    return document.print_document()


def customs_invoice(sales_order_shipment):
    '''
    create a picking_list for a sales_order.
    Loosly based on: 
    http://www.dhl.co.uk/content/dam/downloads/g0/express/
    customs_regulations_russia/export_import_guidelines_to_russia.pdf
    '''
    sales_order = sales_order_shipment.sales_order
    sales_order_shipment_items = sales_order_shipment.salesorderdeliveryitem_set.all()

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
        document.add_table(table_data, [1.0/len(table_data[0])]*len(table_data[0]), 
            bold_header_row=False, line_under_header_row=False, box_line=True)

        ## Invoice and delivery addresses
        document.add_invoice_delivery_headers(
            sales_order.client.printing_address_newlines().replace('\n', '<br></br>'),
            sales_order.ship_to.printing_address_newlines(include_phone=True).replace('\n', '<br></br>'))

        ## Product table
        table_data = [['Product', 'Country of Origin', 'Qty (pieces)', 
            'HS Code', 'Unit Price (EUR)', 'Total Price (EUR)']]
        table_columns_width = [0.3, 0.2, 0.1, 0.25, 0.15]
        total_shipment_value = 0.0
        for prod in sales_order_shipment_items:
            product_name = u'{}, pet {}, art: {}, {}'.format(prod.product.name, 
                prod.product.product_model.umbrella_product_model.get_product_type_display(),
                prod.product.sku,
                prod.product.umbrella_product.export_composition_description)
            sold_item = prod.sales_order_delivery.sales_order.salesorderproduct_set.get(
                price_list_item__product=prod.product)
            table_data.append([product_name, prod.product.umbrella_product.country_of_origin,\
                prod.qty, prod.product.umbrella_product.export_hs_code, sold_item.unit_price, \
                prod.qty * sold_item.unit_price])
            total_shipment_value += prod.qty * sold_item.unit_price
        table_data.append(['', '', '', '', '', ''])    
        table_data.append(['<b>Total price EUR</b>', total_shipment_value, '', '', '', ''])
        table_data.append(['<b>Freight cost EUR</b>', sales_order.transport_cost, '', '', '', ''])
        table_data.append(['<b>Total for payment EUR</b>', 
            total_shipment_value + sales_order.transport_cost,
            '', '', '', ''])
        # table_data.append(['', '', '', '', '', ''])    
        # table_data.append(['<b>Gross Weight</b>', '', '', '', '', ''])    
        document.add_table(table_data, table_columns_width)

        document.add_page_break()

    return document.print_document()    


def commission_report(agent, commission_items, sales_total, commission_total, report_date):
    ''' return pdf with commission report '''
    report = SuzysDocument()

    agent_name = u'{} {}'.format(agent.contact_first_name, agent.contact_name)

    ## title and instructions
    report.add_title(u'Commission report {} {}'.format(
        agent_name,
        report_date.strftime('%d/%m/%Y')))

    ## Commission details
    report.add_heading(u'Commission Detail')
    table_headers = [u'Order #', u'Client Name', u'Date Ordered', u'Date Paid', u'Order Amount']
    col_widths = [0.12, 0.33, 0.18, 0.18, 0.19]
    table_data = []

    table_data.append(table_headers)
    for order in commission_items:
        table_data.append([
            order[u'order #'],
            order[u'client name'],
            order[u'order data'],
            order[u'date paid'],
            order[u'sale total'],
            ])
    report.add_table(table_data, col_widths)

    sales_total = 0
    for s in commission_items:
        sales_total += s[u'sale total']
    report.add_paragraph(u'''Sales total payments received: {}
        Commission owed: {}
        Please send your commission-note to S-Company ltd with this document attached'''.format(
            sales_total,
            commission_total))
    # report.add_paragraph(u'Commission total: {}'.format(commission_total))
    # report.add_paragraph(u'Please send your commission-note to S-Company ltd with this document attached')

    report.add_heading(u'Below our agreed percentages for your information:')
    for tier in agent.agentcommission_set.all():
        report.add_text(u'{}% for sales greater then {}'.format(tier.percentage, tier.from_amount), 'Bullet')


    return report.print_document()
