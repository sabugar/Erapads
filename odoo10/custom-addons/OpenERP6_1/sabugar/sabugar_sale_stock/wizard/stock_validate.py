# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import time

class stock_validate(osv.osv_memory):

    _name = 'stock.validate'

    def validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_obj = self.pool.get('stock.picking')
        for picking in stock_obj.browse(cr, uid, context.get('active_ids'), context):
            if picking.state in ['done', 'cancel']:
                raise osv.except_osv(_('Warning !'),_('You can not validate done and cancel picking.'))
            stock_obj.force_assign(cr, uid, [picking.id])
        self._process_picking(cr, uid, context.get('active_ids'), context)
        return {}

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

stock_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
