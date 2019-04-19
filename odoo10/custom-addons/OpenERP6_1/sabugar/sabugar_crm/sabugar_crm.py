# -*- encoding: utf-8 -*-
from osv import osv,fields
from datetime import *
import time
import calendar
from tools.translate import _
import tools
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _order = 'date_order desc'
    _columns = {
        'o_id': fields.many2one('sale.order', 'Sales Order'),
        'date_order': fields.related('order_id', 'date_order', type='date', store=True, string='Order Date'),
    }
sale_order_line()

class agency_menifest_order(osv.osv):
    _name = 'agency.menifest.order'
    
    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime('%Y-%m-%d', time.strptime(obj.date, DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    _columns = {
        'name': fields.char('Menifest No.', size = 64, readonly=True),
        'sale_ids': fields.one2many('sale.order', 'menifest_id','Sale Orders Ref.', readonly=True),
        'picking_ids': fields.one2many('stock.picking', 'menifest_id', 'Agency Delivery Orders', readonly=True),
        'agency_id' : fields.many2one('sale.shop', 'Agency Name', required=True),
        'date': fields.datetime('Menifest Process Date', readonly=True),
        'date_from':fields.date('Date From', select=True),
        'date_to':fields.date('Date To', select=True),
        'day': fields.function(_day_compute, type='char', string='Day', store=True, select=1, size=32),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        date_from = False
        date_to = False
        domain = []
        if args:
            for arg in args:
                if arg[0] == 'date_from':
                    date_from = arg[2]
                if arg[0] == 'date_to':
                    date_to = arg[2]
        new_args = []
        for d in args:
            if d[0] in ('date_from', 'date_to'):
                continue
            new_args.append(d)
        if date_from and date_to:
            domain = [['date', '>=', date_from], ['date', '<=', date_to]]
        elif date_from:
            domain = [['date', '>=', date_from]]
        elif date_to:
            domain = [['date', '<=', date_to]]
        if domain:
            new_args.extend(domain)
        return super(agency_menifest_order, self).search(cr, uid, new_args, offset, limit, order, context, count)
    
agency_menifest_order()

class runsheet_type(osv.osv):
    _name = "runsheet.type"
    _columns = {
        'name': fields.char('Runsheet Type', size=32, required=True)
    }


class order_runsheet(osv.osv):
    _name = 'order.runsheet'
    
    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime('%Y-%m-%d', time.strptime(obj.date, DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    _columns = {
        'name': fields.char('Runsheet No.', size = 64, readonly=True),
        'sale_ids': fields.one2many('sale.order', 'run_id','Sale Orders Ref.', readonly=True),
        'picking_ids': fields.one2many('stock.picking', 'run_id', 'Agency Delivery Orders', readonly=True),
        'delivery_id':  fields.many2one('res.users','Delivery Responsible', readonly=True),
        'date': fields.datetime('Delivery Scheduled Time', readonly=True),
        'date_from':fields.date('Date From', select=True),
        'date_to':fields.date('Date To', select=True),
        'day': fields.function(_day_compute, type='char', string='Day', store=True, select=1, size=32),
        'type_id': fields.many2one('runsheet.type', 'Runsheet Type', required=True),
        'user_id':  fields.many2one('res.users','Created By', readonly=True),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        date_from = False
        date_to = False
        domain = []
        if args:
            for arg in args:
                if arg[0] == 'date_from':
                    date_from = arg[2]
                if arg[0] == 'date_to':
                    date_to = arg[2]
        new_args = []
        for d in args:
            if d[0] in ('date_from', 'date_to'):
                continue
            new_args.append(d)
        if date_from and date_to:
            domain = [['date', '>=', date_from], ['date', '<=', date_to]]
        elif date_from:
            domain = [['date', '>=', date_from]]
        elif date_to:
            domain = [['date', '<=', date_to]]
        if domain:
            new_args.extend(domain)
        return super(order_runsheet, self).search(cr, uid, new_args, offset, limit, order, context, count)
    
order_runsheet()

class sabugar_crm(osv.osv):
    _inherit = 'crm.lead'
    
    _columns = {
        'phone2': fields.char('Phone 1', size = 64),
        'mobile2': fields.char('Mobile 1', size = 64),
        'city_id': fields.many2one('sabugar.city','City'),
        'area_id': fields.many2one('sabugar.city.area','Area'),
        'referredby': fields.many2one('res.partner',"Referred By"),
        'lead_source': fields.many2one('lead.source','Lead Source'),
        'opportunity_type': fields.many2one('opportunity.type', 'Opportunity Type'),
        'existing_opportunity': fields.many2one('res.partner', 'Existing Partner'),
        'call_center_id': fields.many2one('call.center', 'Call Center'),
        'business_type': fields.selection([('existing','Existing Business'),('new','New Business')],'Business Type'),
        'salesman_name':  fields.many2one('res.users','Caller Name'),
        'phonecall_history_ids' : fields.one2many('crm.phonecall', 'opportunity_id', 'Phone Call History')
    }
    
    def redirect_opportunity_view(self, cr, uid, opportunity_id, context=None):
        models_data = self.pool.get('ir.model.data')

        # Get Opportunity views
        form_view = models_data.get_object_reference(cr, uid, 'sabugar_crm', 'sabugar_crm_case_form_view_oppor')
        tree_view = models_data.get_object_reference(cr, uid, 'sabugar_crm', 'sabugar_crm_case_tree_view_oppor')
        return {
                'name': _('Opportunity'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crm.lead',
                'domain': [('type', '=', 'opportunity')],
                'res_id': int(opportunity_id),
                'view_id': False,
                'views': [(form_view and form_view[1] or False, 'form'),
                          (tree_view and tree_view[1] or False, 'tree'),
                          (False, 'calendar'), (False, 'graph')],
                'type': 'ir.actions.act_window',
        }

    def on_change_opportunity(self,cr, uid, ids,existing_opportunity):
        result = {}    
        opp_ids = self.pool.get('res.partner').read(cr,uid,existing_opportunity)
        result.update({'value': {'name': opp_ids['name']}})
        return result
        
    def on_change_stage(self, cr, uid, ids, stage_id):
        result = {}
        if stage_id:
            stage_ids = self.pool.get('crm.case.stage').read(cr,uid,stage_id)
            if stage_ids['name'] == 'Lost':
                result.update({'value': {'state':'cancel'}})        
            elif stage_ids['name'] == 'Won':
                result.update({'value': {'state': 'done'}})
            else:
                result.update({'value': {'state': 'draft'}})
            stage_id = self.read(cr,uid,stage_id)
        return result
    
sabugar_crm()

class crm_opportunity2phonecall(osv.osv):
    _inherit = 'crm.opportunity2phonecall'
    def default_get(self, cr, uid, fields, context=None):
        res = super(crm_opportunity2phonecall, self).default_get(cr, uid, fields, context=context)
        res.update({'action' : 'schedule'})
        return res
crm_opportunity2phonecall()

class opportunity_type(osv.osv):
    _name = 'opportunity.type'
    
    _columns ={
        'name': fields.char('name', size = 64 ,required=True),
        'code': fields.char('code', size = 64),
    } 
opportunity_type()

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'

    def _get_area_code(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for address in self.browse(cr, uid, ids, context=context):
            res[address.id] = address.city_id.code
        return res
    
    _columns = {
        'phone2': fields.char('Phone 1', size = 64),
        'mobile2': fields.char('Mobile 1', size = 64),
        'city_id': fields.many2one('sabugar.city','City', required=True),
        'area_id': fields.many2one('sabugar.city.area','Area', required=True),
        'referredby':fields.many2one('res.partner',"Referred By"),
        'area_code': fields.function(_get_area_code, type="char", string='Area Code', store=True),
    }
    
#    def name_get(self, cr, user, ids, context=None):
#        if context is None:
#            context = {}
#        if not len(ids):
#            return []
#        res = []
#        reads = self.read(cr, user, ids, ['city_id', 'area_id', 'street'])
#        print "::::",reads,"\n\n"
#        partner_invoice_id = reads[2]
#        for record in reads:
#            if record['area_id']:
#                partner_invoice_id += partner_invoice_id + ', ' +record['area_id'][1]
#            if record['city_id']:
#                partner_invoice_id += partner_invoice_id + ', ' +record['city_id'][1]
#            res.append((record['id'], partner_invoice_id))
#        print "\n\n\n\n\n\nRES :::",res
#        return super(res_partner_address, self).name_get(cr, user, ids, context=context)
    
res_partner_address()

class res_partner(osv.osv):
    _inherit = 'res.partner' 
    
    def _check_name_code(self, cr, uid, ids, context=None):
        """ Checks if Name and area code are unique
        @return: True or False
        """
        for partner in self.browse(cr, uid, ids, context=context):
            partner_ids = self.search(cr, uid, [('name', '=', partner.name), ('area_code', '=', partner.area_code)])
            if len(partner_ids) > 1:
                return False
        return True
    
    def _get_area_code(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = partner.city_id.code
        return res
    
    _columns = {
        'last_transaction': fields.date('Last Transaction Date'),
        'city_id': fields.related('address', 'city_id', type='many2one', relation='sabugar.city',string='City', store=True),
        'area_id': fields.related('address','area_id', type = 'many2one',relation='sabugar.city.area',string='Area', store=True),
        'state' : fields.related('address', 'state_id', type='many2one', relation='res.country.state', string='State', store=True),
        'ref1' : fields.many2one('res.partner', 'Reference'),
        'sales_order_ids': fields.one2many('sale.order', 'partner_id', 'Sales History', readonly=True),
        'opportunity_ids2' : fields.one2many('crm.lead', 'partner_id', 'Opportunity History'),
        'picking_ids' : fields.one2many('stock.picking', 'partner_id', 'Picking History'),
        'customer_source' : fields.many2one('lead.source', 'Customer Source', help="What is the source/medium from this has become customer"),
        #'area_code': fields.related('city_id', 'code',  type='char', string='Area Code', store=True, help="Phone number Area code."),
        'is_agency': fields.boolean('Is Agency?'),
        'area_code': fields.function(_get_area_code, type="char", string='Area Code', store=True),
    }
    
    #_constraints = [ (_check_name_code, 'You must assign a production lot for this product', ['name', 'area_code'])]
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','phone','mobile','area_code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['phone'] and not record['area_code']:
                name = name +' : '+ record['phone']
            elif record['phone'] and record['area_code']:
                name = name +' : '+ record['area_code'] + ' - ' + record['phone']
            elif record['mobile']:
                name = name +' : '+ record['mobile']
            res.append((record['id'], name))
        return res
    
    def name_search(self,cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []
        if name:
            ids = self.search(cr, user, [('name',operator,name)], limit=limit, context=context)
            address_ids = self.pool.get('res.partner.address').search(cr, user, ['|',('mobile2','ilike', name),'|',('phone2','ilike', name),'|',('phone','ilike', name),('mobile','ilike', name)], limit=1111111, context=context)
            if address_ids:
                args += [('address','in',address_ids)]
                ids += self.search(cr, user, args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

res_partner()

class sabugar_city_area(osv.osv):
    _name = 'sabugar.city.area'
    _columns = {
        'name' : fields.char('Area', size= 64,required=True),
        'code' : fields.char('Code', size= 8),
        'city_id': fields.many2one('sabugar.city', 'City'),
    }
    
sabugar_city_area()

class sabugar_city(osv.osv):
    _name = 'sabugar.city'
    _columns = {
        'name' : fields.char('City', size= 64,required=True),
        'code' : fields.char('Code', size= 8), 
    } 
sabugar_city()

class lead_source(osv.osv):
    _name = 'lead.source'
    
    _columns ={
        'name': fields.char('name', size = 64 ,required=True),
        'code': fields.char('code', size = 64),
    } 
lead_source()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = time.strftime('%Y-%m-%d', time.strptime(obj.date_order, '%Y-%m-%d'))
        return res
    
    def _get_line_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        line_obj = self.pool.get('sale.order.line')
        for record in self.browse(cr, uid, ids, context=context):
            lines = line_obj.search(cr, uid, [('order_partner_id', '=', record.partner_id.id), ('state', '<>', 'draft')], limit=5, order='date_order')
            sale_items = [line.id for line in record.order_line]
            all_lines = set(lines) - set(sale_items) 
            result[record.id] = list(all_lines)
        return result
    
    _columns={
        'referredby' :fields.many2one('res.partner',"Referred By", readonly=True, states={'draft': [('readonly', False)]}),
        'opportunity_type': fields.many2one('opportunity.type', 'Customer Type', readonly=True, states={'draft': [('readonly', False)]}),
        'lead_source': fields.many2one('lead.source','Lead Source', readonly=True, states={'draft': [('readonly', False)]}),
        'city_id': fields.many2one('sabugar.city','City', readonly=True, states={'draft': [('readonly', False)]}),
        'area_id': fields.many2one('sabugar.city.area','Area', readonly=True, states={'draft': [('readonly', False)]}),
        'salesman_name':  fields.many2one('res.users','Caller Name', readonly=True, states={'draft': [('readonly', False)]}),
        'group_id': fields.many2one('crm.case.section', "Group", readonly=True, states={'draft': [('readonly', False)]}),
        'landmark': fields.char('Landmark', size= 256, readonly=True, states={'draft': [('readonly', False)]}),
        'street' : fields.char('Address', size=128, readonly=True, states={'draft': [('readonly', False)]}),
        'phone' : fields.char('Phone', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'mobile' : fields.char('Mobile', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'day': fields.function(_day_compute, type='char', string='Day', store=True, select=1, size=32),
        'sequence_id': fields.many2one('ir.sequence.type', 'Series', required=True),
        'name': fields.char('Order Reference', size=64,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),
        'call_date': fields.date('Next Calling Date', select=True, help="Next calling date.", readonly=True, states={'draft': [('readonly', False)]}),
        #'sales_line_ids': fields.function(_get_line_ids, type='many2many', relation="sale.order.line", string="History Sales Lines"),
        #'sales_line_ids': fields.one2many('sale.order.line', 'o_id', 'History Sales Lines'),
        'sales_line_ids': fields.many2many('sale.order.line', 'sale_sale_line_rel', 'o_id', 'l_id', 'History Sales Lines'),
        'date_from':fields.date('Date From', select=True),
        'date_to':fields.date('Date To', select=True),
        'product_id': fields.related('order_line','product_id', type='many2one', relation='product.product', string='Product'),
        'product_category_id': fields.related('order_line','product_id','categ_id', type='many2one', relation='product.category', string='Product Category'),
        'menifest_id': fields.many2one('agency.menifest.order', "Menifest Ref."),
        'run_id': fields.many2one('order.runsheet')
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        date_from = False
        date_to = False
        domain = []
        if args:
            for arg in args:
                if arg[0] == 'date_from':
                    date_from = arg[2]
                if arg[0] == 'date_to':
                    date_to = arg[2]
        new_args = []
        for d in args:
            if d[0] in ('date_from', 'date_to'):
                continue
            new_args.append(d)
        if date_from and date_to:
            domain = [['date_order', '>=', date_from], ['date_order', '<=', date_to]]
        elif date_from:
            domain = [['date_order', '>=', date_from]]
        elif date_to:
            domain = [['date_order', '<=', date_to]]
        if domain:
            new_args.extend(domain)
        return super(sale_order, self).search(cr, uid, new_args, offset, limit, order, context, count)

    
    def schedule_call(self, cr, uid, ids, context=None):
        if context is None: context = {}
        phonecall = self.pool.get('crm.phonecall')
        for order in self.browse(cr, uid, ids, context=context):
            vals = {
                'name': 'Call to %s' % order.partner_id and order.partner_id.name or '',
                'partner_phone': order.phone or '',
                'partner_mobile': order.mobile or '',
                'date': order.call_date or '',
                'partner_id': order.partner_id and order.partner_id.id or False,
            }
             
            phonecall.create(cr, uid, vals, context=context)
        return True
    
    def onchange_partner_id(self,cr, uid, ids,partner_id):
        vals = super(sale_order, self).onchange_partner_id(cr, uid, ids,partner_id)
        if partner_id:
            partner_ids = self.pool.get('res.partner').read(cr,uid,partner_id)
            address_id = self.pool.get('res.partner.address').browse(cr,uid,partner_ids['address'])
            for address in address_id:
                if address.street2:
                    vals['value']['landmark']= address.street2
                if address.city_id.id:
                    vals['value']['city_id']= address.city_id.id
                if address.area_id.id:
                    vals['value']['area_id']= address.area_id.id
                if address.street:
                    vals['value']['street'] = address.street
                if address.phone:
                    vals['value']['phone'] = address.phone
                if address.mobile:
                    vals['value']['mobile'] = address.mobile
            #order_ids = self.search(cr, uid, [('partner_id','=',partner_id)])
            order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_partner_id', '=', partner_id), ('state', '<>', 'draft')], limit=5, order='id')
            print 'order_line_ids>>>>>>>.', order_line_ids
#            if order_line_ids:
#                order_line_list = []
#                #order_id = max(order_ids)
#                order_lines = self.pool.get('sale.order.line').browse(cr, uid, order_line_ids)
#                #order_lines = self.browse(cr, uid, order_id).order_line
#                for line in order_lines:
#                    order_line_dict={
#                        'product_uos_qty': line.product_uos_qty or False,
#                        'procurement_id' : line.procurement_id and line.procurement_id.id or False,
#                        'product_uom' : line.product_uom and line.product_uom.id or False,
#                        'order_id': line.order_id and line.order_id.id or False,
#                        'price_unit' :line.price_unit or False,
#                        'product_uom_qty' : line.product_uom_qty or False,
#                        'discount' : line.discount or False,
#                        'product_uos' : line.product_uos and line.product_uos.id or False,
#                        'invoiced' : line.invoiced or False,
#                        'delay' : line.delay or False,
#                        'name' : line.name,
#                        'notes' : line.notes or False,
#                        'company_id' : line.company_id and line.company_id.id or False,
#                        'salesman_id' : line.salesman_id and line.salesman_id.id or False,
#                        'state' : line.state or False,
#                        'product_id' : line.product_id and line.product_id.id or False,
#                        'order_partner_id' : line.order_partner_id and line.order_partner_id.id or False,
#                        'th_weight' : line.th_weight or False,
#                        'product_packaging' : line.product_packaging or False,
#                        'type' : line.type or False,
#                        'address_allotment_id' :line.address_allotment_id and line.address_allotment_id.id or False
#                    }
#                    order_line_list.append((order_line_dict))
            vals['value']['sales_line_ids'] = sorted(order_line_ids, reverse=True)
        return vals
                            
    def action_ship_create(self, cr, uid, ids, context=None):
        partner_object = self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking')
        for data in self.browse(cr,uid,ids):
            partner_object.write(cr,uid,data.partner_id.id,{'last_transaction' : data.date_order})
        super(sale_order, self).action_ship_create(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            picking_ids= [picking.id for picking in order.picking_ids]
            picking_obj.write(cr, uid, picking_ids, {'salesman_name' : order.salesman_name and order.salesman_name.id or False, 'group_id' : order.group_id and order.group_id.id or False}, context)
        return True
    
    def action_ship_end(self, cr, uid, ids, context=None):
        partner_object = self.pool.get('res.partner')
        now= datetime.now()
        for data in self.browse(cr,uid,ids):
            partner_object.write(cr,uid,data.partner_id.id,{'last_transaction' : now})
        return super(sale_order, self).action_ship_end(cr, uid, ids, context=context)
            
sale_order()

class stock_picking_status(osv.osv):
    _name = 'stock.picking.status'
    _rec_name = 'date'
    _columns = {
        'comment': fields.char('Comment', size=64),
        'date': fields.datetime('Delivery Time', required=True),
        'picking_id': fields.many2one('stock.picking', 'Delivery Order'),
        'shop_id': fields.many2one('sale.shop', 'Agency'),
        'delivery_id': fields.many2one('res.users', 'Delivery Responsible'),
        'sale_id': fields.many2one('sale.order', 'Sales Order Ref'),
        'delivery_category': fields.selection([
                            ('status', 'Delivery Status Update'), ('address_research','Address Research'),
                            ('Inquiry','Inquiry Update'), ('general_update', 'General Update'), ('recovery_update', 'Recovery Update')], 'Delivery Category', select=True),
        'delivery_status': fields.selection([
                            ('damage', 'Shipment Damage'), ('delivered','Shipment Delivered'), ('delivered_partial','Shipment Delivered Partial'),
                            ('not_delivered','Shipment Not Delivered'),('not_delivered_attemp','Shipment Not Delivered - Attempted Delivery'), ('out_delivery', 'Beyond Delivery Area'), ('outof_delivery', 'Shipment Out of Delivery')], 'Delivery Status', select=True),
        'problem_code': fields.selection([
                            ('missed', 'Missed Delivery Schedule'), ('address_incomplete','Address Incomplete/Invalid'), ('incorrect_route','Incorrect Route'),
                            ('office_clode','Business/Office Closed'),('refused','Refused to take'), ('noone_home', 'No One at Home'), ('office_closed', 'Office Closed'),
                            ('no_one_home','Door Lock Home'),('lost','Shipment Lost by Carrier'), ('noone_home', 'No One at Home'), ('office_closed', 'Office Closed')], 'Problem Code', select=True),
        'date_from':fields.datetime('Date From', select=True),
        'date_to':fields.datetime('Date To', select=True),
        
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        date_from = False
        date_to = False
        domain = []
        if args:
            for arg in args:
                if arg[0] == 'date_from' and arg[1] == '>=':
                    date_from = arg[2]
                if arg[0] == 'date_to' and arg[1] == '<=':
                    date_to = arg[2]
        new_args = []
        for d in args:
            if d[0] in ('date_from', 'date_to', '&'):
                continue
            new_args.append(d)
        if date_from and date_to:
            domain = [['date', '>=', date_from], ['date', '<=', date_to]]
        elif date_from:
            domain = [['date', '>=', date_from]]
        elif date_to:
            domain = [['date', '<=', date_to]]
        if domain:
            new_args.extend(domain)
        return super(stock_picking_status, self).search(cr, uid, new_args, offset, limit, order, context, count)
    
stock_picking_status()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
        'landmark': fields.char('Landmark', size= 256),
        'city_id': fields.many2one('sabugar.city','City'),
        'area_id': fields.many2one('sabugar.city.area','Area'),
        'shop_id': fields.many2one('sale.shop','Agency'),
        'salesman_name':  fields.many2one('res.users','Caller Name'),
        'group_id' : fields.many2one('crm.case.section','Group'),
        'date_from':fields.datetime('Date From', select=True),
        'date_to':fields.datetime('Date To', select=True),
        'status_ids': fields.one2many('stock.picking.status', 'picking_id', 'Delivery History'),
        'menifest_id': fields.many2one('agency.menifest.order'),
        'run_id': fields.many2one('order.runsheet')
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        date_from = False
        date_to = False
        domain = []
        if args:
            for arg in args:
                if arg[0] == 'date_from' and arg[1] == '>=':
                    date_from = arg[2]
                if arg[0] == 'date_to' and arg[1] == '<=':
                    date_to = arg[2]
        new_args = []
        for d in args:
            if d[0] in ('date_from', 'date_to', '&'):
                continue
            new_args.append(d)
        if date_from and date_to:
            domain = [['date', '>=', date_from], ['date', '<=', date_to]]
        elif date_from:
            domain = [['date', '>=', date_from]]
        elif date_to:
            domain = [['date', '<=', date_to]]
        if domain:
            new_args.extend(domain)
        return super(stock_picking, self).search(cr, uid, new_args, offset, limit, order, context, count)
    
    def onchange_partner_in(self, cr, uid, ids, address_id):
        result = {}
        if address_id:
            vals = super(stock_picking, self).onchange_partner_in(cr, uid,ids, address_id)
            partner_address = self.pool.get('res.partner.address').read(cr,uid,address_id)
            vals['landmark'] =  partner_address['street2']
            vals['area_id'] =  partner_address['area_id']
            vals['city_id'] =  partner_address['city_id']
            result.update({'value':vals})
        return result 
    
stock_picking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  
