# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import time
from datetime import datetime, timedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class create_menifest(osv.osv_memory):
    
    _name = 'create.menifest'
    _rec_name = 'date'
    
    _columns = {
        'inputs':fields.text('Scanned Orders'),
        'date': fields.datetime('Process Time', required=True, help="Menifest Processing Date"),
        'agency_id' : fields.many2one('sale.shop', 'Agency Name', required=True),
    }
    
    _defaults = {
        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    }
    
    def create_menifest(self,cr, uid, ids, context= None):
        sale_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        menifest_obj = self.pool.get('agency.menifest.order')
        sequence_obj = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        delivery_picking_ids = []
        if context.get('active_ids'):
            delivery_picking_ids = context['active_ids']
        pick_sale_ids = []
        for pickk in picking_obj.browse(cr, uid, delivery_picking_ids):
            if pickk.sale_id:
                pick_sale_ids.append(pickk.sale_id.id)
        
        for wizard in self.browse(cr, uid, ids, context=context):
            input = wizard.inputs
            if input:
                orders = input.split()
                for order in orders:
                    sale_ids = sale_obj.search(cr, uid, [('name', '=', order)])
                    if sale_ids:
                        sale_id = sale_ids[0]
                        pick_sale_ids.append(sale_id)
                        sale = sale_obj.browse(cr, uid, sale_id, context=context)
                        picking_ids = picking_obj.search(cr, uid, [('sale_id', '=', sale.id), ('type', '=', 'internal')])
                        if picking_ids:
                            delivery_picking_ids.extend(picking_ids)
            for picking in picking_obj.browse(cr, uid, list(set(delivery_picking_ids)), context=context):
                if picking.shop_id.id != wizard.agency_id.id:
                    raise osv.except_osv(_('Warning!'),
                    _('Selected Sales Order number (%s) does not belong to Agency: "%s".') % (sale.name, wizard.agency_id.name))
            vals = {
                    'name': sequence_obj.get(cr, uid, 'agency.menifest.order') or '/',
                    'sale_ids': [(4, s) for s in list(set(pick_sale_ids))],
                    'picking_ids': [(4, p) for p in list(set(delivery_picking_ids))],
                    'agency_id': wizard.agency_id.id,
                    'date': wizard.date,
            }
            menifest_obj.create(cr, uid, vals, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
create_menifest()


class delivery_order_update(osv.osv_memory):
    
    _name = 'delivery.order.update'
    _rec_name = 'date'
    
    _columns = {
        'comment': fields.char('Comment', size=64),
        'inputs':fields.text('Scanned Orders'),
        'date': fields.datetime('Delivery Time', required=True, help="Delivery Date"),
        'delivery_category': fields.selection([
                            ('status', 'Delivery Status Update'), ('address_research','Address Research'),
                            ('Inquiry','Inquiry Update'), ('general_update', 'General Update'), ('recovery_update', 'Recovery Update')], 'Delivery Category', select=True, required=True),
        'delivery_status': fields.selection([
                            ('damage', 'Shipment Damage'), ('delivered','Shipment Delivered'), ('delivered_partial','Shipment Delivered Partial'),
                            ('not_delivered','Shipment Not Delivered'),('not_delivered_attemp','Shipment Not Delivered - Attempted Delivery'), ('out_delivery', 'Beyond Delivery Area'), ('outof_delivery', 'Shipment Out of Delivery')], 'Delivery Status', select=True),
        'problem_code': fields.selection([
                            ('missed', 'Missed Delivery Schedule'), ('address_incomplete','Address Incomplete/Invalid'), ('incorrect_route','Incorrect Route'),
                            ('office_clode','Business/Office Closed'),('refused','Refused to take'), ('noone_home', 'No One at Home'), ('office_closed', 'Office Closed'),
                            ('no_one_home','Door Lock Home'),('lost','Shipment Lost by Carrier'), ('noone_home', 'No One at Home'), ('office_closed', 'Office Closed')], 'Problem Code', select=True),
        
    }
    
    _defaults = {
        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    }
    
    def update_status(self,cr, uid, ids, context= None):
        sale_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        status_obj = self.pool.get('stock.picking.status')
        sequence_obj = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        delivery_picking_ids = []
        if context.get('active_ids'):
            delivery_picking_ids = context['active_ids']
        for wizard in self.browse(cr, uid, ids, context=context):
            input = wizard.inputs
            if input:
                orders = input.split()
                for order in orders:
                    sale_ids = sale_obj.search(cr, uid, [('name', '=', order)])
                    if sale_ids:
                        sale_id = sale_ids[0]
                        sale = sale_obj.browse(cr, uid, sale_id, context=context)
                        pick_ids = picking_obj.search(cr, uid, [('sale_id', '=', sale.id), ('type', '=', 'out'), ('state', '=', 'assigned')])
                        picking_ids = delivery_picking_ids + pick_ids
                        for picking in picking_obj.browse(cr, uid, list(set(picking_ids)), context=context):
                            vals = {
                                'delivery_status': wizard.delivery_status or False,
                                'delivery_category': wizard.delivery_category or False,
                                'problem_code': wizard.problem_code or False,
                                'sale_id': sale.id,
                                'picking_id': picking.id,
                                'shop_id': picking.shop_id.id,
                                'delivery_id': picking.delivery_id.id,
                                'date': wizard.date,
                                'comment': wizard.comment
                            }
                            status_obj.create(cr, uid, vals, context=context)
                            if wizard.delivery_status and wizard.delivery_status == 'delivered':
                                picking_obj.action_done(cr, uid, [picking.id], context=context)
                                move_obj.action_done(cr, uid, [move.id for move in picking.move_lines], context=context)
        return {'type': 'ir.actions.act_window_close'}

delivery_order_update()


class order_runsheet_wizard(osv.osv_memory):
    
    _name = 'order.runsheet.wizard'
    
    _columns = {
        'inputs':fields.text('Scanned Orders'),
        'delivery_id': fields.many2one('res.users', 'Delivery User', required=True),
        'date': fields.datetime('Delivery Time', required=True, help="Delivery Time should be assigned +/- 1 hour from current time."),
        'type_id': fields.many2one('runsheet.type', 'Runsheet Type', required=True),
    }
    
    _defaults = {
        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    }
    
    def issue(self,cr, uid, ids, context= None):
        sale_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        runsheet_obj = self.pool.get('order.runsheet')
        sequence_obj = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        delivery_picking_ids = []
        if context.get('active_ids'):
            delivery_picking_ids = context['active_ids']
        pick_sale_ids = []
        for pickk in picking_obj.browse(cr, uid, delivery_picking_ids):
            if pickk.sale_id:
                pick_sale_ids.append(pickk.sale_id.id)
        for wizard in self.browse(cr, uid, ids, context=context):
            current_time = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            date1 = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)
            date2 = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S') + timedelta(hours=-1)
            if (wizard.date > str(date1) or wizard.date < str(date2)):
                raise osv.except_osv(_('Invalid Date !'), _('You can assign date only +/- 1 hours from current time')) 
            input = wizard.inputs
            if input:
                orders = input.split()
                for order in orders:
                    sale_ids = sale_obj.search(cr, uid, [('name', '=', order)])
                    if sale_ids:
                        sale_id = sale_ids[0]
                        pick_sale_ids.append(sale_id)
                        sale = sale_obj.browse(cr, uid, sale_id, context=context)
                        pick_ids = picking_obj.search(cr, uid, [('sale_id', '=', sale.id), ('type', '=', 'out'), ('state', '=', 'assigned')])
                        if pick_ids:
                            delivery_picking_ids.extend(pick_ids)
            vals = {
                'name': sequence_obj.get(cr, uid, 'order.runsheet') or '/',
                'sale_ids': [(4, s) for s in list(set(pick_sale_ids))],
                'picking_ids': [(4, p) for p in list(set(delivery_picking_ids))],
                'delivery_id': wizard.delivery_id.id,
                'date': wizard.date,
                'type_id': wizard.type_id.id,
                'user_id': uid
            }
            runsheet_obj.create(cr, uid, vals, context=context)
        return {'type': 'ir.actions.act_window_close'}

    
    
order_runsheet_wizard()

class scan_order(osv.osv_memory):
    
    _name = 'scan.order'
    
    _columns = {
        'inputs':fields.text('Scanned Orders'),
    }
    
    def run_orders(self,cr, uid, ids, context= None):
        sale_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        if context is None:
            context = {}
        delivery_picking_ids = []
        if context.get('active_ids'):
            delivery_picking_ids = context['active_ids']
        for wizard in self.browse(cr, uid, ids, context=context):
            input = wizard.inputs
            if input:
                orders = input.split()
                for order in orders:
                    sale_ids = sale_obj.search(cr, uid, [('name', '=', order), ('state', 'not in', ['draft', 'done', 'cancel'])])
                    if sale_ids:
                        sale_id = sale_ids[0]
                        sale = sale_obj.browse(cr, uid, sale_id, context=context)
                        pick_ids = picking_obj.search(cr, uid, [('sale_id', '=', sale.id), ('type', '=', 'internal')])
                        picking_ids = delivery_picking_ids + pick_ids
                        for picking in picking_obj.browse(cr, uid, list(set(picking_ids)), context=context):
                            picking_obj.force_assign(cr, uid, [picking.id])
                        self._process_picking(cr, uid, pick_ids, context)
        return {'type': 'ir.actions.act_window_close'}


    def get_picking_type(self, cr, uid, picking, context=None):
        picking_type = picking.type
        for move in picking.move_lines:
            if picking.type == 'in' and move.product_id.cost_method == 'average':
                picking_type = 'in'
                break
            else:
                picking_type = 'out'
        return picking_type

    def _process_picking(self, cr, uid, picking_ids, context=None):
        if context is None:
            context = {}
        pick_obj = self.pool.get('stock.picking')
        
        partial_datas = {
            'delivery_date' : time.strftime('%Y-%m-%d %H:%M:%S')
        }

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)

            for move in pick.move_lines:
                partial_datas['move%s' % (move.id)] = {
                    'product_id': move.product_id.id, 
                    'product_qty': move.product_qty, 
                    'product_uom': move.product_uom.id, 
                    'prodlot_id': move.prodlot_id.id, 
                }
                if (picking_type == 'in') and (move.product_id.cost_method == 'average'):
                    partial_datas['move%s' % (move.id)].update({
                                                    'product_price' : move.product_id.standard_price, 
                                                    'product_currency': move.product_id.company_id and move.product_id.company_id.currency_id and move.product_id.company_id.currency_id.id or False, 
                                                    })
        pick_obj.do_partial(cr, uid, picking_ids, partial_datas, context=context)
        return True
            
    
scan_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
