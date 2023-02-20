frappe.ui.form.on("Stock Reconciliation", {
  refresh: function (frm) {
    if (frm.doc.docstatus < 1) {
      frm.add_custom_button(__("Fetch Items from Item Group"), function () {
        frm.events.get_items_but_item_group(frm);
      });
    }
  },

  get_items_but_item_group: function (frm) {
    let fields = [
      {
        label: 'Item Group',
        fieldname: 'item_group',
        fieldtype: 'Link',
        options: 'Item Group',
        reqd: 1,
        "get_query": function () {
          return {
            "filters": {
              "company": frm.doc.company,
            }
          };
        }
      },
      {
        label: "Item Code",
        fieldname: "item_code",
        fieldtype: "Link",
        options: "Item",
        "get_query": function () {
          return {
            "filters": {
              "disabled": 0,
            }
          };
        }
      },
      {
        label: __("Ignore Empty Stock"),
        fieldname: "ignore_empty_stock",
        fieldtype: "Check"
      }
    ];

    frappe.prompt(fields, function (data) {
      frappe.call({
        method: "stock_reconcialiation_per_item_group.controllers.stock_reconcialiation_per_item_group.get_items",
        args: {
          item_group: data.item_group,
          posting_date: frm.doc.posting_date,
          posting_time: frm.doc.posting_time,
          company: frm.doc.company,
          ignore_empty_stock: data.ignore_empty_stock
        },
        callback: function (r) {
          if (r.exc || !r.message || !r.message.length) return;

          frm.clear_table("items");

          r.message.forEach((row) => {
            let item = frm.add_child("items");
            $.extend(item, row);

            item.qty = item.qty || 0;
            item.valuation_rate = item.valuation_rate || 0;
          });
          frm.refresh_field("items");
        }
      });
    }, __("Get Items"), __("Update"));
  },
});
