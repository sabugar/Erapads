{
    "name": "Stock Balance Report",
    "version": "1.0",
    "depends": ["stock"],
    "author": "Serpent Consulting Services",
    "category": "Warehouse",
    "description": """
    **************Stock Balance Report*****************
    This Module Provide Report for Balancing Existing stock What stock is in and out from the warehouse
    based on given range.
    """,
    'update_xml': ['wizard/stock_range_view.xml','report/stock_balance_report_view.xml'],
    'demo_xml': [],
    'installable': True,
    'auto_install':False,
    'application':True,
}