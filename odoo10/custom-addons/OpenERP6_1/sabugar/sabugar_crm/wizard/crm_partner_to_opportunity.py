# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _

class crm_partner2opportunity(osv.osv_memory):

    _inherit = 'crm.partner2opportunity'

    _columns = {
        'name' : fields.char('Opportunity Name', size=64),
        'planned_revenue': fields.float('Expected Revenue', digits=(16,2)),
        'call_center_id': fields.many2one('res.partner', 'Call-Center'),
        'salesman_id': fields.many2one('res.users', 'Salesman'),
    }

    def make_opportunity(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        lead_obj = self.pool.get('crm.lead')
        stage_obj = self.pool.get('crm.case.stage')
        models_data = self.pool.get('ir.model.data')
        opportunity_ids = []
        if context.get('active_ids'):
            partner_ids = context.get('active_ids', [])
            for data in self.browse(cr, uid, ids, context):
                for partner in partner_obj.browse(cr, uid, context.get('active_ids'), context=context):
                    stage_ids = stage_obj.search(cr, uid, [('name', '=', 'New')])
                    address = partner.address and partner.address[0] or False
                    vals = {
                        'name' : partner.name,
                        'area_id': address and address.area_id and address.area_id.id or False, 
                        'city_id': address and address.city_id and address.city_id.id or False,
                        'partner_address_id': address and address.id or False, 
                        'street': address and address.street or False, 
                        'partner_id': partner.id, 
                        'call_center_id': data.call_center_id and data.call_center_id.id or False,
                        'user_id': data.salesman_id and data.salesman_id.id or False,
                        'zip': address and address.zip or False,
                        'title': address and address.title and address.title.id or False,
                        'partner_name': partner.name,
                        'planned_revenue': data.planned_revenue,
                        'country_id': address and address.country_id and address.country_id.id or False, 
                        'type': 'opportunity',
                        'function': address and address.function or False,
                        'fax': address and address.fax or False, 
                        'description': partner.comment or False, 
                        'street2': address and address.street2 or False,
                        'phone': address and address.phone or False, 
                        'stage_id': stage_ids and stage_ids[0] or False, 
                        'mobile': address and address.mobile or False,
                        'state_id': address and address.state_id and address.state_id.id or False, 
                        'email_from': address and address.email or False,
                        'state' :'draft',
                    }
                    opportunity_ids.append(lead_obj.create(cr, uid, vals, context=context))
        form_view = models_data.get_object_reference(cr, uid, 'sabugar_crm', 'sabugar_crm_case_form_view_oppor')
        tree_view = models_data.get_object_reference(cr, uid, 'sabugar_crm', 'sabugar_crm_case_tree_view_oppor')
        return {
                'name': _('Opportunity'),
                'domain': [('id', 'in', opportunity_ids)],
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crm.lead',
                'view_id': False,
                'views': [(tree_view and tree_view[1] or False, 'tree'),
                          (form_view and form_view[1] or False, 'form'),
                          (False, 'calendar'), (False, 'graph')],
                'type': 'ir.actions.act_window',
        }

crm_partner2opportunity()

class crm_partner2phonecall(osv.osv_memory):
    
    _name = 'crm.partner2phonecall'
    
    _columns = {
        'assign_to':fields.many2one('res.users', 'Assign to'),
        'date': fields.date('Date'),
    }
    
    def assign_call(self,cr, uid, ids, context= None):
        if context is None:
            context = {}
        partner_obj = self.pool.get('res.partner')
        phone_call_object = self.pool.get('crm.phonecall')
        models_data = self.pool.get('ir.model.data')
        call_list = []
        if context.get('active_ids'):
            for data in self.browse(cr, uid, ids, context):
                for partner in partner_obj.browse(cr, uid, context.get('active_ids'), context=context):
                    call_summary = 'Call to %s'%partner.name
                    vals = {
                        'name': call_summary,
                        'partner_phone': partner.phone or False,
                        'date': data.date or False,
                        'user_id':data.assign_to.id or False,
                        'partner_id': partner.id or False,
                        'partner_mobile': partner.mobile or False,
                    }
                    call_list.append(phone_call_object.create(cr, uid, vals, context=context))
        form_view = models_data.get_object_reference(cr, uid, 'crm', 'crm_case_phone_form_view')
        tree_view = models_data.get_object_reference(cr, uid, 'crm', 'crm_case_phone_tree_view')
        
        return {
                'name': _('Scheduled CallS'),
                'domain': [('id', 'in', call_list)],
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crm.phonecall',
                'view_id': False,
                'views': [(tree_view and tree_view[1] or False, 'tree'),
                          (form_view and form_view[1] or False, 'form')],
                'type': 'ir.actions.act_window',
        }
            
    
crm_partner2phonecall()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
