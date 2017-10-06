from printing.documents import SuzysDocument

def picking_list(production_order):
	'''create a picking_list for a production_order'''

	document = SuzysDocument()

	document.add_title('Picking List {}'.format(production_order))

	document.add_invoice_delivery_headers(
		production_order.invoice_to,
		production_order.ship_to)

