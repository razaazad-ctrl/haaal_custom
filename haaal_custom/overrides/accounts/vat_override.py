import frappe

@frappe.whitelist()
def test_vat_override():
    return "HAAAL VAT Override Load Successfully"
