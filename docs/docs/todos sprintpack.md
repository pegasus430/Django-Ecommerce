# Questions sprintpack

- PreAdvice, what is dit?
	`Aankondigen van goederen`
- AddOrder,
    * Partial delivery, when would this happen > shouldnt happen if all is in stock before forwarding the order



# Todos Sprintpack

- Create sprintpack log models to monitor any request after execution.
- Invoice or picking-list, create list of EU countries, or else invoice.
- For orders, create shipping extension.
- For orders, allow for cancel, and create credit notes  (remainder of items)
- For orders, create picking-lists and proforma invoices.
- For products, add stock extension like on materials
- Allow to add notes to any model in the system with a mixin, or by default override model.
- integrate rest of things
- customs codes: 
	* 6307 9099 geconfectioneerde artikelen van weefsel andere overige
	* 4016 1000 Werken van schuimrubber
	* 9404 9090 Bed products


## Api integration
> CreateProduct = Done
> CreatePreAdvice = Done
> CreateOrder = Generate invoices
> RequestOrderStatus = Done
> RequestInventory = Done