# How does a sale work?

1. Add client
2. Add order > Draft
3. Create invoice  (via xero) > Invoice Created
4. Send invoice > Invoice Sent
4. Check payment condition
	- if 0 days, wait for payment 
		- if payed, go to delivery > Ready for delivery
		- if not payed, wait for payment > Waiting for payment
	- if > 0 days, go to delivery > Ready for delivery
5. Delivery
	- If stock, Deliver > Ship
	- if no stock, wait > Waiting for stock


## Todos
- Add checking for payments in Xero, and update invoice
- Add HUEY for hourly checks and shipments
