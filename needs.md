# Update for Odoo DW API

## For `/dwapi/orders`

The result should only be individual ready packs, where there can be multiple results for one 'order_name' but the pack ID is unique.

## For `/dwapi/order/<order_name>`

In the order details we want:

- The pick, pack, and out id for the result
- The residual amount on the order

For each commercial invoice line:

- A 'shippable' field for if the item is a shippable thing, eg. No Rush, UPS, Admin Shipping, Discounts, etc are all False, whereas actual items are True
- A quantity for how many of the item has been packed already
