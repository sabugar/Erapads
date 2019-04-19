# -*- coding: utf-8 -*-

from osv import osv

class change_location(osv.osv_memory):
    _name = 'change.location'

    def action_ok(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_obj = self.pool.get('stock.picking')
        picking_ids = stock_obj.search(cr, uid, [('state', '=', 'done'), ('type', '=', 'out')])
        for picking in stock_obj.browse(cr, uid, picking_ids, context):
            if picking.sale_id and picking.sale_id.shop_id and picking.shop_id and picking.sale_id.shop_id.id != picking.shop_id.id:
                location_id = picking.shop_id.warehouse_id.lot_stock_id.id
                move_ids = [move.id for move in picking.move_lines]
                if move_ids:
                    cr.execute("update stock_move set location_id=%s where id in (%s)" % (location_id,  ','.join(map(str, move_ids))))
        return {}

change_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
