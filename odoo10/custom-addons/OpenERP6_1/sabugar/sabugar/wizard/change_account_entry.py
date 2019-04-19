# -*- coding: utf-8 -*-

from osv import osv

class change_account_entry(osv.osv_memory):
    _name = 'change.account.entry'

    def action_ok(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_obj = self.pool.get('stock.picking')
        move_line_obj = self.pool.get('account.move.line')
        picking_ids = stock_obj.search(cr, uid, [('state', '=', 'done'), ('type', '=', 'out')])
        for picking in stock_obj.browse(cr, uid, picking_ids, context):
            if picking.sale_id:
                move_line_ids = move_line_obj.search(cr, uid, [('ref', '=', picking.origin), ('partner_id', '=', picking.sale_id.shop_id.agencies_id.id)])
                if move_line_ids and picking.shop_id and picking.sale_id.shop_id.agencies_id:
                    new_partner_id = picking.shop_id.agencies_id.id
                    cr.execute("update account_move_line set partner_id=%s where id in (%s)" % (new_partner_id,  ','.join(map(str, move_line_ids))))
                    move_line_acc_ids = move_line_obj.search(cr, uid, [('id', 'in', move_line_ids), ('account_id', '=', picking.sale_id.shop_id.agencies_id.property_account_receivable.id)])
                    if move_line_acc_ids:
                        new_account_id = picking.shop_id.agencies_id.property_account_receivable.id
                        cr.execute("update account_move_line set account_id=%s where id in (%s)" % (new_account_id,  ','.join(map(str, move_line_acc_ids))))
        return {}

change_account_entry()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
