# -*- coding: utf-8 -*-

{
    "name" : "Sabugar Sale Stock",
    "version" : "1.0",
    "author" : "Serpent Consulting Services",
    "category" : "Sale",
    "website" : "http://www.serpentcs.com",
    "description": """
    """,
    'author': 'SerpentCS',
    'depends': ['sale', 'stock'],
    'init_xml': [],
    'update_xml': [
        'sabugar_sale_stock_view.xml',
        'sabugar_sale_stock_report.xml',
        'wizard/stock_validate_view.xml',
        'wizard/stock_easy_process_view.xml'
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
