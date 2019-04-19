from osv import fields, osv
from tools.translate import _
import time

class crm_make_sale(osv.osv_memory):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'close': fields.boolean('Close Opportunity', help='Check this to close the opportunity after having created the sale order.'),
    }
    
    _defaults = {
        'partner_id': False
    }

    def makeOrder(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []
        models_data = self.pool.get('ir.model.data')
        for make in self.browse(cr, uid, ids, context=context):
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not case.partner_id:
                    continue
                partner = case.partner_id
                pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                fpos = partner.property_account_position and partner.property_account_position.id or False
                partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                        ['default', 'invoice', 'delivery', 'contact'])
                pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Data Insufficient!'), _('Customer has no addresses defined!'))
                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'shop_id': make.shop_id and make.shop_id.id or False,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_order_id': partner_addr['contact'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': time.strftime('%Y-%m-%d'),
                    'fiscal_position': fpos,
                    'lead_source': case.lead_source and case.lead_source.id or False,
                    'landmark':case.street2,
                    'area_id': case.area_id and case.area_id.id or False, 
                    'city_id': case.city_id and case.city_id.id or False,
                    'group_id': case.section_id and case.section_id.id or False,
                    'call_center_id': case.call_center_id and case.call_center_id.id or False,
                    'opportunity_type': case.opportunity_type and case.opportunity_type.id or False,
                    'salesman_name' : case.salesman_name and case.salesman_name.id or False,
                    'street' : case.street or False,
                    'phone' : case.phone or False,
                    'mobile' : case.mobile or False,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
            form_view = models_data.get_object_reference(cr, uid, 'sabugar_crm', 'sabugar_view_order_form')
            tree_view = models_data.get_object_reference(cr, uid, 'sale', 'view_order_tree')
            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view and tree_view[1] or False, 'tree'),
                          (form_view and form_view[1] or False, 'form'),
                          (False, 'calendar'), (False, 'graph')],
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view and tree_view[1] or False, 'tree'),
                          (form_view and form_view[1] or False, 'form'),
                          (False, 'calendar'), (False, 'graph')],
                    'res_id': new_ids
                }
            return value

crm_make_sale() 