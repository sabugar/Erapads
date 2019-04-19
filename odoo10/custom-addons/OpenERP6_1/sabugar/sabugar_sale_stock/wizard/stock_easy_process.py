# -*- coding: utf-8 -*-
from osv import fields, osv

class stock_easy_process(osv.osv_memory):

    _name = "stock.easy.process"
    _description = "Easily Force Availability on a shipment"

    def process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        for data in self.browse(cr, uid, ids, context=context):
            force_assign = []
            action = []
            for picking in picking_obj.browse(cr, uid, context.get('active_ids'), context):
                if picking.state in ['confirmed']:
                    force_assign.append(picking.id)
                action.append(picking.id)
            if force_assign:
                picking_obj.force_assign(cr, uid, force_assign, context)
            if action:
                picking_obj.action_move(cr, uid, action, context)
        return {'type': 'ir.actions.act_window_close'}

stock_easy_process()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
