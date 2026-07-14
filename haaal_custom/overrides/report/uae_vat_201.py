from erpnext.regional.report.uae_vat_201.uae_vat_201 import execute as original_execute


def execute(filters=None):
    """
    Wrapper around the standard ERPNext UAE VAT 201 report.
    """
    columns, data = original_execute(filters)

    # We will modify 'data' later.

    return columns, data
