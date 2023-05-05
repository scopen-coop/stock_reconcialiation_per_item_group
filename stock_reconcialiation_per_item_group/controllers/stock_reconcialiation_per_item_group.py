# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
    get_item_data, get_items_for_stock_reco, get_itemwise_batch)
from erpnext.stock.utils import get_stock_balance
from frappe.utils import cint


@frappe.whitelist()
def get_items(
	item_group, posting_date, posting_time, company, ignore_empty_stock=False
):
	bin = frappe.qb.DocType("Bin")
	item = frappe.qb.DocType("Item")
	wh = frappe.qb.DocType("Warehouse")

	query = (
		frappe.qb.from_(bin)
		.inner_join(item)
		.on(bin.item_code == item.item_code)
		.inner_join(wh)
		.on(wh.name == bin.warehouse)
		.where(bin.actual_qty != 0)
		.where(item.item_group == item_group)
		.select(item.item_code, wh.name)
	)

	if company:
		query = query.where(wh.company == company)

	datas = query.run()

	res = []
	if datas is not None:
		for data in datas:
			ignore_empty_stock = cint(ignore_empty_stock)
			items = [frappe._dict({"item_code": data[0], "warehouse": data[1]})]

			if not data[0]:
				items = get_items_for_stock_reco(data[1], company)

			itemwise_batch_data = get_itemwise_batch(data[1], posting_date, company, data[0])

			for d in items:
				if d.item_code in itemwise_batch_data:
					valuation_rate = get_stock_balance(
						d.item_code,
						d.warehouse,
						posting_date,
						posting_time,
						with_valuation_rate=True,
					)[1]

					for row in itemwise_batch_data.get(d.item_code):
						if ignore_empty_stock and not row.qty:
							continue

						args = get_item_data(row, row.qty, valuation_rate)
						res.append(args)
				else:
					stock_bal = get_stock_balance(
						d.item_code,
						d.warehouse,
						posting_date,
						posting_time,
						with_valuation_rate=True,
						with_serial_no=cint(d.has_serial_no),
					)
					qty, valuation_rate, serial_no = (
						stock_bal[0],
						stock_bal[1],
						stock_bal[2] if cint(d.has_serial_no) else "",
					)

					if ignore_empty_stock and not stock_bal[0]:
						continue

					args = get_item_data(d, qty, valuation_rate, serial_no)

					res.append(args)

		return res
