# -*- Coding: utf-8 -*-

{   'name': "ERA Sanitary Pads",
    'summary': """Customization for ERA Sanitary Pad business""",
    'description': """Module Customization
                    - Base - Partner
                    - Sale
                    - Inventory
                    - Account""",
    'author': 'Sueb Sabugar',
    'company': 'Not decided',
    'website': 'http://www.google.com',
    'category': 'Sanitary Pad',
    'version': "10.0.1.0.0",
    'application': True,
    'installable': True,
    'auto_install': False,
    'depends': ['base', 'stock', 'sale'],
    'data': [
        'views/res_partner.xml',
        'security/ir.model.access.csv',
        'views/sales_view.xml',
        ],
}
