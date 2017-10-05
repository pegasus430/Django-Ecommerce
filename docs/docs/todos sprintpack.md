# Questions sprintpack

- PreAdvice, what is dit?
	`Aankondigen van goederen`
- AddOrder,
    * Partial delivery, when would this happen > shouldnt happen if all is in stock before forwarding the order
- CreateProduct
    * to create a product, the api needs a ‘product item’  But where can I see how this if formed? 
    `(p10) ===> Page 19`


# Todos Sprintpack

- Create sprintpack log models to monitor any request after execution.
- Invoice or picking-list, create list of EU countries, or else invoice.
- For orders, create shipping extension.
- For orders, allow for cancel, and create credit notes  (remainder of items)
- For orders, create picking-lists and proforma invoices.
- For products, add stock extension like on materials
- Allow to add notes to any model in the system with a mixin, or by default override model.
- integrate rest of things


## Api integration
> CreateProduct = Done
> CreatePreAdvice = Done
> CreateOrder
> RequestOrderStatus
> RequestInventory = Done


