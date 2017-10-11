import datetime

from operator import itemgetter

from printing_tools.documents import SuzysDocument


def commission_report(agent):
    ''' return pdf with commission report '''
    report = SuzysDocument()

    order_list, commission_total = agent.comission_owed()
    sorted_order_list = sorted(order_list, key=lambda k: k['order data']) 

    agent_name = u'{} {}'.format(agent.contact_first_name, agent.contact_name)

    ## title and instructions
    report.add_title(u'Commission report {} {}'.format(
        agent_name,
        datetime.date.today().strftime('%d/%m/%Y')))

    ## Commission details
    report.add_heading(u'Commission Detail')
    table_headers = [u'Order #', u'Client Name', u'Date Ordered', u'Date Paid', u'Order Amount']
    col_widths = [0.12, 0.33, 0.18, 0.18, 0.19]
    table_data = []

    table_data.append(table_headers)
    for order in sorted_order_list:
        table_data.append([
            order[u'order #'],
            order[u'client name'],
            order[u'order data'],
            order[u'date paid'],
            order[u'sale total'],
            ])
    report.add_table(table_data, col_widths)

    sales_total = 0
    for s in order_list:
        sales_total += s[u'sale total']
    report.add_body_text(u'Sales total: {}'.format(sales_total))
    report.add_body_text(u'Commission total: {}'.format(commission_total))
    report.add_body_text(u'Please send your commission-note to S-Company ltd with this document attached')

    report.add_heading(u'Below our agreed percentages for your information:')
    for tier in agent.agentcommission_set.all():
        report.add_text(u'{}% for sales greater then {}'.format(tier.percentage, tier.from_amount), 'Bullet')


    return report.print_document()