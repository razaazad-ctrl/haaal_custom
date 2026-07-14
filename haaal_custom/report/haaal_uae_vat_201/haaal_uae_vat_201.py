import frappe

from erpnext.regional.report.uae_vat_201.uae_vat_201 import (
    execute as original_execute,
)


def execute(filters=None):

    columns, data = original_execute(filters)

    input_total = get_input_total(filters)
    input_vat = get_input_vat(filters)

    replace_standard_expenses(data, input_total, input_vat)

    add_net_vat_section(data)

    return columns, data


def get_input_total(filters):

    conditions = [
        "pi.docstatus = 1",
        "tax.account_head LIKE 'VAT%'",
    ]

    values = {}

    if filters.get("company"):
        conditions.append("pi.company=%(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    result = frappe.db.sql(
        f"""
        SELECT
            SUM(pi.base_net_total)
        FROM
            `tabPurchase Invoice` pi
        INNER JOIN
            `tabPurchase Taxes and Charges` tax
                ON tax.parent=pi.name
        WHERE
            {' AND '.join(conditions)}
        """,
        values,
    )

    return result[0][0] or 0


def get_input_vat(filters):

    conditions = [
        "pi.docstatus=1",
        "tax.account_head LIKE 'VAT%'",
    ]

    values = {}

    if filters.get("company"):
        conditions.append("pi.company=%(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    result = frappe.db.sql(
        f"""
        SELECT
            SUM(tax.base_tax_amount)
        FROM
            `tabPurchase Invoice` pi
        INNER JOIN
            `tabPurchase Taxes and Charges` tax
                ON tax.parent=pi.name
        WHERE
            {' AND '.join(conditions)}
        """,
        values,
    )

    return result[0][0] or 0


def replace_standard_expenses(data, total, vat):

    for row in data:

        if row.get("title") == "Standard Rated Expenses":

            row["total"] = frappe.format(total, {"fieldtype": "Currency"})
            row["tax_amount"] = frappe.format(vat, {"fieldtype": "Currency"})


def add_net_vat_section(data):

    data.append({})

    data.append(
        {
            "title": "Net VAT Due",
        }
    )

    data.append(
        {
            "vat_rate": "",
            "title": "Total Value of Due Tax for the Period",
            "total": "",
            "tax_amount": "",
        }
    )