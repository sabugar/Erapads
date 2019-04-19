# -*- encoding: utf-8 -*-
{
    'name': 'sabugar_crm',
    'version': '1.0',
    'category': 'Customer Relationship Management',
    'description': 
    '''
    ''',
    'author': 'Serpent Consulting services',
    'website': 'http://www.serpentcs.com',
    'depends': [
        'crm','sale_crm','sabugar_sale_stock','mass_editing'
    ],
    'update_xml':[
        'wizard/scan_delivery_orders.xml',
        'sabugar_crm_view.xml',
        'sabugar_print_label.xml',
        'wizard/crm_partner_to_opportunity_view.xml',
        'wizard/opportunity_convert_to_quote_view.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: